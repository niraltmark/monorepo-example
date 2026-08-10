# All dependency wiring for the todos-service is handled directly via
# Depends(TodoRepository) inside TodoService.__init__ and
# Depends(TodoService) inside each route handler.
# No additional wrapper functions or Annotated aliases are needed.
