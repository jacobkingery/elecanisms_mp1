#include <p24FJ128GB206.h>
#include "config.h"
#include "common.h"
#include "pin.h"
#include "timer.h"
#include "oc.h"

int16_t main(void) {
    init_clock();
    init_pin();
    init_timer();
    init_oc();

    pin_digitalOut(&D[8]);  // IN1
    pin_digitalOut(&D[7]);  // IN2
    pin_digitalOut(&D[5]);  // IN3
    pin_digitalOut(&D[6]);  // IN4

    timer_setPeriod(&timer2, 2.0);
    timer_start(&timer2);

    pin_clear(&D[7]);
    oc_pwm(&oc1, &D[8], NULL, 10.0, 32768);

    while (1) {
        if (timer_flag(&timer2)) {
            timer_lower(&timer2);
        }
    }
}

