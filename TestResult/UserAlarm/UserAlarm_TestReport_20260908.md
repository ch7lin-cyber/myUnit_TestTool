# UserAlarm Unit Test Report

- Test item: `app_fb_user_alarm()`
- Test author: OpenAI Codex
- DUT author: CH
- Tested at: 2026-09-08 05:06:28 UTC
- Tested source commit: `b4ad09c824f238f6d97db51e01d4ed8c1ef28066`
- Host compiler: GCC, C11
- Runtime checks: AddressSanitizer and UndefinedBehaviorSanitizer
- Random seed: `20260903`

## Result

**FUNCTIONAL PASS WITH FINDINGS**

The executable completed successfully:

```text
PASS 10027 checks (including 5000 deterministic random vectors)
```

Covered behavior:

- Mode 0–8 and invalid Mode
- Strict boundary behavior (`>` and `<`; equality does not trigger)
- High/low hysteresis entry, latch and release
- Standby arming at `SV ± 10`
- Invert, Hold and Peak options
- Clear bit consumption and preservation of unrelated bits
- Two independent FB instances
- 5,000 deterministic random vectors compared with a reference decision model
- Repeatability for equal initial state and inputs

## Findings

1. **No Init API** — callers must initialize `alarmLatch`, `standbyReady`, `peakH` and `peakL` correctly. Uninitialized peak values produce unreliable records.
2. **No NULL validation** — `fb`, `Clear` or `out` being NULL causes invalid memory access. The current API has no error-code contract.
3. **No parameter-range validation** — negative or inconsistent `AlarmH/AlarmL` values are accepted. Legal engineering ranges must be supplied before formal out-of-range acceptance testing can be complete.
4. **Invalid Mode is silent** — any Mode outside 0–8 behaves as DISABLE, with the same return value as a valid call.
5. **Return value is always 1** — it cannot distinguish success, invalid configuration or pointer error.
6. **Strict conversion warnings** — the two clear operations use unsigned masks on an `int16_t` target and produce four `-Wsign-conversion` warnings:
   `(*Clear) &= ~ALARM_CLEAR_RESET` and `(*Clear) &= ~ALARM_CLEAR_PEAK`.
7. **Latch has two responsibilities** — `alarmLatch` is shared by hysteresis modes and HOLD. Switching modes can therefore carry latch history into another behavior unless the caller clears it.

## Acceptance limitation

This report proves consistency with the current implementation and the observable interface. It does not yet prove compliance with a product requirement because PV/SV units, legal ranges, AlarmH/AlarmL constraints, invalid-input policy and formal expected return/error codes were not provided.
