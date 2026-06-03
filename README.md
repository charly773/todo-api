# todo-api

API REST simple con Flask, PostgreSQL y Docker Compose.

## Ejecutar con Docker

```sh
docker compose up -d
```

La API estará disponible en:

- http://localhost:5001/
- http://localhost:5001/todos

## Endpoints

- GET /
- GET /todos
- POST /todos

Ejemplo para crear una tarea:

```sh
curl -X POST http://localhost:5001/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"Tarea"}'
```

