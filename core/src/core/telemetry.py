"""Common OpenTelemetry configuration helpers."""

from __future__ import annotations

from typing import Final

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

_PROVIDER_STATE: Final = {"configured": False}


def configure_tracing(app: FastAPI, *, service_name: str = "documents-api") -> None:
    """Instrument the provided FastAPI application with a console exporter."""

    if not _PROVIDER_STATE["configured"]:
        resource = Resource.create({"service.name": service_name})
        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(tracer_provider)
        _PROVIDER_STATE["configured"] = True
    else:
        tracer_provider = trace.get_tracer_provider()

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
