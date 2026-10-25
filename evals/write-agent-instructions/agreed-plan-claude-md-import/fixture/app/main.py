from fastapi import FastAPI

app = FastAPI(title="Quillnote API")


@app.get("/health")
async def health() -> dict[str, bool]:
    return {"ok": True}
