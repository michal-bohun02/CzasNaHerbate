const easeInOutCubic = (progress: number) =>
  progress < 0.5
    ? 4 * progress * progress * progress
    : 1 - Math.pow(-2 * progress + 2, 3) / 2;

const getScrollRoot = () =>
  document.scrollingElement ?? document.documentElement;

let activeAnimationId: number | null = null;

export const smoothScrollToElement = (
  element: HTMLElement,
  duration = 1000,
) => {
  const scrollRoot = getScrollRoot();
  const startY = scrollRoot.scrollTop;
  const targetY = element.getBoundingClientRect().top + startY;
  const distance = targetY - startY;

  if (Math.abs(distance) < 1) return;

  if (activeAnimationId !== null) {
    cancelAnimationFrame(activeAnimationId);
  }

  let startTime: number | null = null;

  const step = (timestamp: number) => {
    if (startTime === null) startTime = timestamp;

    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);

    scrollRoot.scrollTop = startY + distance * easeInOutCubic(progress);

    if (progress < 1) {
      activeAnimationId = requestAnimationFrame(step);
    } else {
      activeAnimationId = null;
    }
  };

  activeAnimationId = requestAnimationFrame(step);
};
