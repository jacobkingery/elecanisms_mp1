#include <p24FJ128GB206.h>
#include "config.h"
#include "common.h"
#include "pin.h"
#include "timer.h"
#include "oc.h"
#include "md.h"

int16_t main(void) {
    init_clock();
    init_timer();
    init_pin();
    init_oc();
    init_md();

    timer_setPeriod(&timer2, 1.0);
    timer_start(&timer2);

    uint16_t s = 0xFFFF;
    uint8_t d = 0;

    md_velocity(&mdp, 0x6000 & s, d);

    uint8_t flag = 1;
    while (1) {
        if (timer_flag(&timer2)) {
            timer_lower(&timer2);
            s = ~s;
            if (flag) {
                d = !d;
            }
            md_velocity(&mdp, 0x6000 & s, d);
            flag = !flag;
        }
    }
}
