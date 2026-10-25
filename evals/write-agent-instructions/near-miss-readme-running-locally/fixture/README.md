# labelkit

Web tool for labelling image datasets for object detection. Exports COCO and YOLO formats.

## Running locally

You need Docker.

    docker compose up --build

Then open http://localhost:8000. The first start downloads the sample dataset (~200 MB).

## Configuration

Settings come from environment variables:

- `LABELKIT_DATA_DIR` — where images and annotations live (default `./data`)
- `LABELKIT_EXPORT_FORMAT` — `coco` or `yolo` (default `coco`)

## License

MIT
