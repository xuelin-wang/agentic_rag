"""OpenTelemetry configuration for the documents service."""

from __future__ import annotations

from typing import Final

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

_CONFIGURED: Final = {"provider": False}


def configure_tracing(app: FastAPI) -> None:
    """Set up tracing with a console exporter and instrument the FastAPI app."""

    if not _CONFIGURED["provider"]:
        resource = Resource.create({"service.name": "documents-api"})
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(tracer_provider)
        _CONFIGURED["provider"] = True
    else:
        tracer_provider = trace.get_tracer_provider()

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
