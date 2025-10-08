export function debounce<T extends (...args: any[]) => void>(fn: T, wait = 400) {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return (...args: Parameters<T>) => {
    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(() => {
      timeout = null
      fn(...args)
    }, wait)
  }
}
