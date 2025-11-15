+"""Minimal informational ringdown toolkit in a single file.
+
+This module provides a light-weight implementation of the
+telegraph-based reinterpretation described in the accompanying
+manuscript.  The interface is intentionally compact so that the entire
+workflow—parameter declaration, diffusivity computation, and reporting—
+fits in a single file for quick experimentation or educational demos.
+
+Usage
+-----
+Run the script directly for an interactive prompt or import the
+``summarize_event`` helper from other notebooks and scripts::
+
+    $ python ringdown.py --event GW150914
+    $ python ringdown.py --custom tau-ms=4.0 freq-hz=251
+
+"""
+from __future__ import annotations
+
+import argparse
+import dataclasses
+import json
+from typing import Dict, Iterable, Optional
+
+from astropy import units as u
+
+C = 299_792_458 * u.m / u.s
+
+
+@dataclasses.dataclass(frozen=True)
+class RingdownEvent:
+    """Container for phenomenological ringdown parameters."""
+
+    name: str
+    tau_220: u.Quantity  # dominant damping time
+    freq_220: u.Quantity  # dominant mode frequency
+    reference: str
+
+    def diffusivity(self) -> u.Quantity:
+        """Return the informational diffusivity ``D = c^2 tau``."""
+
+        return (C ** 2 * self.tau_220).to(u.m ** 2 / u.s)
+
+    def characteristic_speed(self) -> u.Quantity:
+        """Characteristic propagation speed implied by the telegraph model."""
+
+        return (self.diffusivity() / self.tau_220) ** 0.5
+
+    def as_dict(self) -> Dict[str, str]:
+        return {
+            "event": self.name,
+            "tau_220": f"{self.tau_220.to(u.ms):.3f}",
+            "freq_220": f"{self.freq_220.to(u.Hz):.1f}",
+            "diffusivity": f"{self.diffusivity():.3e}",
+            "characteristic_speed": f"{self.characteristic_speed().to(u.m / u.s):.6e}",
+            "reference": self.reference,
+        }
+
+
+def load_catalogue() -> Dict[str, RingdownEvent]:
+    """Return a minimal catalogue of canonical events."""
+
+    return {
+        "GW150914": RingdownEvent(
+            name="GW150914",
+            tau_220=4.0 * u.ms,
+            freq_220=251 * u.Hz,
+            reference="Abbott et al. (2016, PRL 116, 061102)",
+        ),
+        "GW170104": RingdownEvent(
+            name="GW170104",
+            tau_220=5.0 * u.ms,
+            freq_220=200 * u.Hz,
+            reference="Abbott et al. (2017, PRL 118, 221101)",
+        ),
+        "GW190521": RingdownEvent(
+            name="GW190521",
+            tau_220=5.5 * u.ms,
+            freq_220=190 * u.Hz,
+            reference="Abbott et al. (2020, PRL 125, 101102)",
+        ),
+    }
+
+
+def summarize_event(event: RingdownEvent) -> str:
+    lines = [
+        f"Event: {event.name}",
+        f"Reference: {event.reference}",
+        f"Tau_220: {event.tau_220.to(u.ms):.3f}",
+        f"Freq_220: {event.freq_220.to(u.Hz):.1f}",
+        f"Diffusivity (D=c^2 tau): {event.diffusivity():.3e}",
+        f"Characteristic speed: {event.characteristic_speed().to(u.m / u.s):.6e}",
+    ]
+    return "\n".join(lines)
+
+
+def parse_custom_event(args: argparse.Namespace) -> Optional[RingdownEvent]:
+    if args.custom is None:
+        return None
+
+    params: Dict[str, float] = {}
+    for item in args.custom:
+        key, value = item.split("=", 1)
+        params[key.strip()] = float(value)
+
+    try:
+        tau_ms = params["tau_ms"]
+        freq_hz = params["freq_hz"]
+    except KeyError as exc:
+        missing = ", ".join(sorted(set(["tau_ms", "freq_hz"]) - params.keys()))
+        raise SystemExit(f"Missing required parameter(s): {missing}") from exc
+
+    return RingdownEvent(
+        name=args.name or "Custom",
+        tau_220=tau_ms * u.ms,
+        freq_220=freq_hz * u.Hz,
+        reference="User-specified posterior sample",
+    )
+
+
+def iter_events(catalogue: Dict[str, RingdownEvent], names: Iterable[str]) -> Iterable[RingdownEvent]:
+    if not names:
+        return catalogue.values()
+
+    for name in names:
+        try:
+            yield catalogue[name]
+        except KeyError as exc:
+            raise SystemExit(f"Unknown event '{name}'. Available: {', '.join(catalogue)}") from exc
+
+
+def cli(argv: Optional[Iterable[str]] = None) -> None:
+    parser = argparse.ArgumentParser(description="Compute informational diffusivity for GW ringdown events.")
+    parser.add_argument("--event", action="append", dest="events", help="Evaluate a built-in event by name.")
+    parser.add_argument(
+        "--custom",
+        nargs="+",
+        help="Supply custom posterior parameters as tau_ms=<value> freq_hz=<value>.",
+    )
+    parser.add_argument("--name", help="Optional label for a custom event.")
+    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
+    args = parser.parse_args(argv)
+
+    catalogue = load_catalogue()
+    selected = list(iter_events(catalogue, args.events or []))
+    custom = parse_custom_event(args)
+    if custom is not None:
+        selected.append(custom)
+
+    if not selected:
+        parser.error("No events specified. Use --event or --custom to provide parameters.")
+
+    if args.json:
+        print(json.dumps([event.as_dict() for event in selected], indent=2))
+    else:
+        for event in selected:
+            print(summarize_event(event))
+            print()
+
+
+if __name__ == "__main__":
+    cli()
 
EOF
)
