#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#define MY_API
#include "../../DUT/L04_FB/UserAlarm/userAlarm.h"

static int failures;
#define CHECK(x) do { if (!(x)) { fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #x); failures++; } } while (0)

static int call_alarm(APP_ALARM_FB_T *fb, int pv, int sv, int mode, int ah, int al,
                      int *clear, int option, APP_ALARM_FB_OUT_T *out)
{
    int16_t clear16 = (int16_t)*clear;
    uint16_t result = app_fb_user_alarm(fb, (int16_t)pv, (int16_t)sv, (int16_t)mode,
        (int16_t)ah, (int16_t)al, &clear16, (uint8_t)option, out);
    *clear = clear16;
    return result;
}

static APP_ALARM_FB_T fresh(void)
{
    APP_ALARM_FB_T fb = {false, false, INT16_MIN, INT16_MAX};
    return fb;
}

static void test_modes_and_boundaries(void)
{
    APP_ALARM_FB_OUT_T out;
    int clear = 0;
    APP_ALARM_FB_T fb = fresh();

    CHECK(call_alarm(&fb, 999, 1000, ALARM_MODE_DISABLE, 10, 10, &clear, 0, &out) == 1);
    CHECK(out.AlarmOutput == 0);

    fb = fresh();
    call_alarm(&fb, 1010, 1000, ALARM_MODE_REL_HL, 10, 10, &clear, 0, &out);
    CHECK(out.AlarmOutput == 0);
    call_alarm(&fb, 1011, 1000, ALARM_MODE_REL_HL, 10, 10, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 989, 1000, ALARM_MODE_REL_HL, 10, 10, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);

    fb = fresh();
    call_alarm(&fb, 1011, 1000, ALARM_MODE_REL_H, 10, 10, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 989, 1000, ALARM_MODE_REL_L, 10, 10, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);

    fb = fresh();
    call_alarm(&fb, 100, 0, ALARM_MODE_ABS_HL, 100, 0, &clear, 0, &out);
    CHECK(out.AlarmOutput == 0);
    call_alarm(&fb, 101, 0, ALARM_MODE_ABS_H, 100, 0, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, -1, 0, ALARM_MODE_ABS_L, 100, 0, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);

    call_alarm(&fb, 999, 1000, 99, 10, 10, &clear, 0, &out);
    CHECK(out.AlarmOutput == 0);
}

static void test_hysteresis(void)
{
    APP_ALARM_FB_OUT_T out;
    int clear = 0;
    APP_ALARM_FB_T fb = fresh();

    call_alarm(&fb, 1011, 1000, ALARM_MODE_HYS_H, 10, 5, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 1005, 1000, ALARM_MODE_HYS_H, 10, 5, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 1004, 1000, ALARM_MODE_HYS_H, 10, 5, &clear, 0, &out);
    CHECK(out.AlarmOutput == 0);

    fb = fresh();
    call_alarm(&fb, 989, 1000, ALARM_MODE_HYS_L, 10, 5, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 995, 1000, ALARM_MODE_HYS_L, 10, 5, &clear, 0, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 996, 1000, ALARM_MODE_HYS_L, 10, 5, &clear, 0, &out);
    CHECK(out.AlarmOutput == 0);
}

static void test_options_and_clear(void)
{
    APP_ALARM_FB_OUT_T out;
    int clear = 0;
    APP_ALARM_FB_T fb = fresh();

    call_alarm(&fb, 1200, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_STANDBY, &out);
    CHECK(out.AlarmOutput == 0 && !fb.standbyReady);
    call_alarm(&fb, 1000, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_STANDBY, &out);
    CHECK(out.AlarmOutput == 0 && fb.standbyReady);
    call_alarm(&fb, 1200, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_STANDBY, &out);
    CHECK(out.AlarmOutput == 1);

    fb = fresh();
    call_alarm(&fb, 1000, 1000, ALARM_MODE_DISABLE, 0, 0, &clear, ALARM_OPT_INVERT, &out);
    CHECK(out.AlarmOutput == 1);

    fb = fresh();
    call_alarm(&fb, 1200, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_HOLD, &out);
    CHECK(out.AlarmOutput == 1);
    call_alarm(&fb, 1000, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_HOLD, &out);
    CHECK(out.AlarmOutput == 1);
    clear = ALARM_CLEAR_RESET | 0x40;
    call_alarm(&fb, 1000, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_HOLD, &out);
    CHECK(out.AlarmOutput == 0 && clear == 0x40);

    fb = fresh();
    call_alarm(&fb, 10, 0, ALARM_MODE_DISABLE, 0, 0, &clear, ALARM_OPT_PEAK, &out);
    call_alarm(&fb, 20, 0, ALARM_MODE_DISABLE, 0, 0, &clear, ALARM_OPT_PEAK, &out);
    call_alarm(&fb, -5, 0, ALARM_MODE_DISABLE, 0, 0, &clear, ALARM_OPT_PEAK, &out);
    CHECK(out.PeakH == 20 && out.PeakL == -5);
    clear = ALARM_CLEAR_PEAK;
    call_alarm(&fb, 7, 0, ALARM_MODE_DISABLE, 0, 0, &clear, ALARM_OPT_PEAK, &out);
    CHECK(out.PeakH == 7 && out.PeakL == 7 && clear == 0);
}

static void test_multi_instance(void)
{
    APP_ALARM_FB_OUT_T oa, ob;
    int clear = 0;
    APP_ALARM_FB_T a = fresh(), b = fresh();
    call_alarm(&a, 1200, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_HOLD, &oa);
    call_alarm(&b, 1000, 1000, ALARM_MODE_REL_H, 10, 10, &clear, ALARM_OPT_HOLD, &ob);
    CHECK(oa.AlarmOutput == 1 && ob.AlarmOutput == 0 && !b.alarmLatch);
}

static int expected_alarm(int pv, int sv, int mode, int ah, int al)
{
    switch (mode) {
    case 0: return 0;
    case 1: return (pv > sv + ah) || (pv < sv - al);
    case 2: return pv > sv + ah;
    case 3: return pv < sv - al;
    case 4: return (pv > ah) || (pv < al);
    case 5: return pv > ah;
    case 6: return pv < al;
    default: return 0;
    }
}

static void test_random_and_determinism(void)
{
    unsigned seed = 20260903U;
    for (int i = 0; i < 5000; i++) {
        seed = seed * 1664525U + 1013904223U;
        int pv = (int)(seed % 4001U) - 2000;
        seed = seed * 1664525U + 1013904223U;
        int sv = (int)(seed % 3001U) - 1500;
        int mode = (int)(seed % 7U);
        int ah = (int)((seed >> 8) % 201U);
        int al = (int)((seed >> 16) % 201U);
        int clear = 0;
        APP_ALARM_FB_T a = fresh(), b = fresh();
        APP_ALARM_FB_OUT_T oa, ob;
        call_alarm(&a, pv, sv, mode, ah, al, &clear, 0, &oa);
        clear = 0;
        call_alarm(&b, pv, sv, mode, ah, al, &clear, 0, &ob);
        CHECK(oa.AlarmOutput == expected_alarm(pv, sv, mode, ah, al));
        CHECK(oa.AlarmOutput == ob.AlarmOutput);
    }
}

int main(void)
{
    test_modes_and_boundaries();
    test_hysteresis();
    test_options_and_clear();
    test_multi_instance();
    test_random_and_determinism();

    if (failures != 0) {
        printf("FAIL %d\n", failures);
        return 1;
    }
    puts("PASS 10027 checks (including 5000 deterministic random vectors)");
    return 0;
}
