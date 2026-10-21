def test_build_workflow_compiles():
    from app.graph.workflow import build_workflow
    workflow = build_workflow()
    assert workflow is not None
