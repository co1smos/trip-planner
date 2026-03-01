


from app.agent.graph import build_graph
from app.models.state import AgentState
from app.store.run_store import RunStore
from app.trace.tracer import new_trace_id

class WorkflowRunner:
    def __init__(self, store: RunStore):
        self.store = store
        self.graph = build_graph()
    
    async def run_workflow(self, run_id: str) -> None:
        # update record status 
        record = await self.store.load_run(run_id)
        if record is None:
            raise ValueError(f"run_id not found: {run_id}")
        record.status = "RUNNING"
        await self.store.save_run(record)

        # Initialize state 
        state = AgentState(
            run_id=run_id,
            trace_id=new_trace_id(),
            request=record.request,
            category=None,
            plan_steps=[],
            observations=[],
            result=None,
            last_node=None,
            errors=[],
        )

        last_state: AgentState | None = None

        try:
            async for state_dict in self.graph.astream(state.model_dump(), stream_mode="values"):
                cur_state = AgentState.model_validate(state_dict)

                if (
                    last_state is None
                    or (cur_state.last_node and cur_state.last_node != last_state.last_node)
                ):
                    await self.store.save_state(cur_state)
                    last_state = cur_state

            if last_state is not None and last_state.last_node == "synthesize":
                record.status = "SUCCEEDED"
                record.result = last_state.result
            else:
                record.status = "FAILED"
                record.errors = ({"errors": last_state.errors} if last_state else {"node": "unknown", "msg": "no state"})

        except Exception as e:
            # failure: persist FAILED + error info
            record.status = "FAILED"
            record.errors = {
                "node": last_state.last_node if last_state else "unknown",
                "type": type(e).__name__,
                "msg": str(e),
            }
            await self.store.save_run(record)
            raise

        await self.store.save_run(record)
