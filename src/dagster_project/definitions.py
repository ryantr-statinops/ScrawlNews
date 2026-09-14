import dagster as dg


@dg.asset(group_name="shadow")
def shadow_pipeline_ready(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
    """Safe smoke asset; real news assets are added in the shadow migration."""
    context.log.info("Dagster shadow foundation is ready")
    return dg.MaterializeResult(metadata={"telegram_sent": 0, "domain_db_mutated": False})


defs = dg.Definitions(assets=[shadow_pipeline_ready])
