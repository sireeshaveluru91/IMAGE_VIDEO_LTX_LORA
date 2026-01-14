"""Entry point for running LTX image-to-video workflows locally."""

from pathlib import Path
from typing import Optional

import typer

from pipeline.config import load_config
from pipeline.runner import generate_video
from pipeline.sagemaker import submit_async_invocation

app = typer.Typer(help="Utilities for LTX image-to-video experimentation.")


@app.command()
def run(
    config_path: Path = typer.Argument(Path("configs/default.yaml"), help="Path to the run configuration."),
    output_dir: Path = typer.Option(Path("outputs"), help="Directory for rendered videos and logs."),
    dry_run: bool = typer.Option(False, help="Print the resolved config without executing."),
) -> None:
    """Load configuration, validate settings, and hand off to the execution pipeline."""
    cfg = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        typer.secho(cfg.model_dump_json(indent=2), fg=typer.colors.CYAN)
        return

    typer.secho(f"Ready to run LTX pipeline with prompt: {cfg.prompt}", fg=typer.colors.GREEN)
    typer.secho(f"Assets will be written to {output_dir}", fg=typer.colors.GREEN)

    result = generate_video(cfg, output_dir)
    typer.secho(f"Result written to: {result}", fg=typer.colors.BLUE)


@app.command()
def validate(config_path: Optional[Path] = typer.Argument(None)) -> None:
    """Validate project configuration to ensure deployment readiness."""
    cfg = load_config(config_path or Path("configs/default.yaml"))
    typer.secho("Configuration looks valid.", fg=typer.colors.GREEN)
    typer.secho(
        f"Model checkpoint: {cfg.model.checkpoint}\nTarget fps: {cfg.render.fps}\nDuration: {cfg.render.duration_seconds}s",
        fg=typer.colors.BLUE,
    )


@app.command()
def pose(
    pose: str = typer.Option("tree", help="Pose name: tree|warrior|other"),
    config_path: Path = typer.Argument(Path("configs/default.yaml"), help="Path to the run configuration."),
    output_dir: Path = typer.Option(Path("outputs"), help="Directory for rendered videos and logs."),
) -> None:
    """Generate a simple yoga-pose video (placeholder renderer)."""
    cfg = load_config(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    typer.secho(f"Generating yoga pose '{pose}'...", fg=typer.colors.GREEN)
    from pipeline.runner import generate_yoga_pose_video

    result = generate_yoga_pose_video(cfg, output_dir, pose=pose)
    typer.secho(f"Pose video written to: {result}", fg=typer.colors.BLUE)
    

@app.command("sagemaker-async")
def sagemaker_async(
    endpoint_name: str = typer.Option(..., prompt=True, help="Name of the SageMaker async endpoint."),
    config_path: Path = typer.Option(Path("configs/default.yaml"), help="Path to the run configuration."),
    staging_dir: Path = typer.Option(Path("outputs/async_payloads"), help="Local folder for staged payloads."),
    input_bucket: Optional[str] = typer.Option(None, help="Override input S3 bucket; defaults to cfg.aws.s3_bucket."),
    output_bucket: Optional[str] = typer.Option(None, help="Override output S3 bucket; defaults to cfg.aws.s3_bucket."),
    input_prefix: str = typer.Option("async-inputs", help="S3 prefix for pending payloads."),
    output_prefix: str = typer.Option("async-outputs", help="S3 prefix where the endpoint writes results."),
    prompt_override: Optional[str] = typer.Option(None, help="Optional prompt override without editing the YAML."),
    wait: bool = typer.Option(True, help="Wait for the endpoint to finish and report the first artifact."),
    poll_interval: int = typer.Option(15, help="Seconds between S3 checks when waiting."),
    timeout_seconds: int = typer.Option(900, help="Maximum seconds to wait for an async result."),
) -> None:
    """Submit the current config to a SageMaker Async Inference endpoint."""

    cfg = load_config(config_path)
    overrides = {"prompt": prompt_override} if prompt_override else None

    handle = submit_async_invocation(
        cfg,
        endpoint_name=endpoint_name,
        staging_dir=staging_dir,
        input_bucket=input_bucket,
        output_bucket=output_bucket,
        input_prefix=input_prefix,
        output_prefix=output_prefix,
        wait_for_completion=wait,
        poll_interval=poll_interval,
        timeout_seconds=timeout_seconds,
        payload_overrides=overrides,
    )

    typer.secho(f"Submitted async request {handle.inference_id} to {handle.endpoint_name}", fg=typer.colors.GREEN)
    typer.secho(f"Input payload: {handle.input_s3_uri}", fg=typer.colors.BLUE)
    typer.secho(f"Output prefix: {handle.output_location}", fg=typer.colors.BLUE)

    if handle.completed_output:
        typer.secho(f"Async result available at: {handle.completed_output}", fg=typer.colors.MAGENTA)


if __name__ == "__main__":
    app()
