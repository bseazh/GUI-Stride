# PDF 转换说明

## 已完成的文件

1. **GUI-Stride技术说明文档.md** - 完整的技术文档 Markdown 源文件
2. **GUI-Stride技术说明文档.html** - 已转换的 HTML 格式文档
3. **convert_to_pdf.bat** - Windows 批处理文件，用于快速打开 HTML 文件

## 如何生成 PDF 文档

### 方法一：使用批处理文件（推荐）
双击运行 `docs/convert_to_pdf.bat` 文件，它会自动：
1. 在默认浏览器中打开 HTML 文档
2. 显示转换说明

### 方法二：手动操作
1. 用浏览器打开 `docs/GUI-Stride技术说明文档.html`
2. 按 `Ctrl + P` 打开打印对话框
3. 选择打印机：
   - **Chrome/Edge**: 选择"另存为PDF"
   - **Firefox**: 选择"Microsoft Print to PDF"
4. 设置打印选项：
   - 布局：纵向
   - 纸张大小：A4
   - 页边距：普通
   - 背景图形：已启用（保留颜色）
5. 点击"保存"按钮生成 PDF 文件

### 方法三：使用 PDF 转换工具
可以使用以下工具将 HTML 转换为 PDF：
- Pandoc（需要额外安装）
- wkhtmltopdf
- Adobe Acrobat

## 文件说明

- **Markdown 源文件**：用于编辑和版本控制
- **HTML 文件**：可在浏览器中直接查看，支持打印
- **PDF 文件**：最终交付文档，格式固定，适合打印和分发

## 注意事项

1. 确保 HTML 文件在浏览器中完全加载后再进行打印
2. 使用"背景图形"选项可以保留文档中的颜色和格式
3. PDF 文件可能需要在 Adobe Acrobat 或其他 PDF 查看器中进行最终校对

## 技术支持

如果在转换过程中遇到问题，请检查：
1. 浏览器是否支持打印为 PDF 功能
2. 系统是否有足够的磁盘空间
3. 文件权限是否正确