declare module 'docx-preview' {
  export interface DocxRenderOptions {
    className?: string
    inWrapper?: boolean
    ignoreWidth?: boolean
    ignoreHeight?: boolean
    useBase64URL?: boolean
  }

  export function renderAsync(
    data: ArrayBuffer | Blob,
    container: HTMLElement,
    styleOptions?: unknown,
    renderOptions?: DocxRenderOptions
  ): Promise<void>
}
