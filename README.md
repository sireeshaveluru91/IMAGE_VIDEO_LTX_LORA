# image_video_LTX_LORA

VS Code workspace for running, containerizing, and deploying LTX image-to-video workloads with an eye toward future LoRA fine-tuning.

## Project Goals
- Baseline local inference pipeline driven by config files and Typer CLI commands.
- Docker images optimized for CUDA and ready for AWS SageMaker Async Inference.
- Infrastructure folder for Terraform/CDK/IaC stubs plus automation scripts.
- Documentation and requirements tracking for LoRA adapters and dataset hygiene.

## Getting Started
1. Create an environment (uv, venv, or conda) with Python 3.10+.
2. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
3. Copy `.env.template` to `.env` and fill in AWS + tracking secrets.
4. Run a dry-run config check:
   ```bash
   make dry-run
   ```
5. Once the real LTX checkpoint is available, update `configs/default.yaml` and trigger `make run`.

## Makefile Targets
- `make setup` – install dependencies and pre-commit hooks.
- `make fmt` / `make lint` – formatting and quality gates.
- `make dry-run` – ensure configs load correctly without GPU time.
- `make docker-build` – build the CUDA-enabled image tagged for ECR.
- `make test` – run pytest suite.

## Repository Layout
- `src/` – Typer CLI entry points, config models, and soon the inference pipeline.
- `configs/` – YAML configs per environment or prompt batch.
- `notebooks/` – exploratory data/model notebooks (kept empty by default).
- `docker/` – Dockerfiles, entrypoints, and compose helpers.
- `infra/` – IaC stubs for AWS resources (S3, SageMaker, monitoring).
- `scripts/` – automation helpers for dataset sync, ECR pushes, etc.
- `tests/` – pytest-based regression tests.
- `docs/` – requirements and future design docs.

## Next Steps
- Flesh out the actual LTX pipeline logic and logging.
- Author Docker + SageMaker integration scripts.
- Extend docs for LoRA dataset prep and fine-tune scheduling.

## SageMaker Helpers
- Submit Async jobs directly from this repo with `python -m main sagemaker-async --endpoint-name <name>`.
- Stage payloads in `outputs/async_payloads/` and automatically upload them to S3 for the endpoint.
- Deploy or refresh Async endpoints using `python scripts/sagemaker_endpoint.py --image-uri <ECR URI> --role-arn <ARN> --async-output-s3 s3://bucket/prefix` plus any desired overrides.
