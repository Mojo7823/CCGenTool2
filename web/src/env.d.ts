/// <reference types="vite/client" />

declare module 'html-to-docx' {
  const htmlToDocx: (
    html: string,
    fileName?: string,
    options?: Record<string, unknown>
  ) => Promise<ArrayBuffer>
  export default htmlToDocx
}

declare module 'docx-preview' {
  export function renderAsync(
    data: ArrayBuffer | Blob | Uint8Array,
    container: HTMLElement,
    styleContainer?: HTMLElement | null,
    options?: Record<string, unknown>
  ): Promise<void>
}
