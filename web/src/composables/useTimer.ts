import { ref, onUnmounted, computed } from 'vue'

export const useTimer = () => {
    const elapsedTime = ref(0)
    const startTime = ref(0)
    let timerId: number

    const update = () => {
        elapsedTime.value = Date.now() - startTime.value
    }

    const startTimer = () => {
        startTime.value = Date.now()
        elapsedTime.value = 0
        timerId = window.setInterval(update, 1000)
    }

    const stopTimer = () => {
        window.clearInterval(timerId)
    }

    onUnmounted(stopTimer)

    return {
        elapsedTime,
        startTimer,
        stopTimer,
    }
}