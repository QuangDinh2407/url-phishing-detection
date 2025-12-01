"""
Script để đọc file Word và tạo báo cáo với caption và mô tả cho mỗi hình ảnh
"""
import os
from docx import Document
from pathlib import Path

def read_docx_and_create_report(docx_path, output_path=None):
    """
    Đọc file Word và tạo báo cáo với caption và mô tả cho mỗi hình ảnh
    
    Parameters:
    -----------
    docx_path : str
        Đường dẫn đến file Word
    output_path : str, optional
        Đường dẫn để lưu file báo cáo (mặc định: cùng thư mục với file Word)
    """
    print(f"📖 Đang đọc file: {docx_path}")
    
    # Đọc file Word
    doc = Document(docx_path)
    
    # Tạo nội dung báo cáo
    report_lines = []
    report_lines.append("# BÁO CÁO THỰC HÀNH\n")
    report_lines.append("=" * 80 + "\n\n")
    
    image_count = 0
    current_paragraph_text = ""
    
    # Duyệt qua tất cả các đoạn và hình ảnh
    for i, paragraph in enumerate(doc.paragraphs):
        text = paragraph.text.strip()
        
        # Kiểm tra xem có hình ảnh trong đoạn này không
        if paragraph.runs:
            has_image = False
            for run in paragraph.runs:
                if run._element.xpath('.//a:blip'):
                    has_image = True
                    break
            
            if has_image:
                image_count += 1
                # Thêm caption cho hình ảnh
                if text:
                    report_lines.append(f"## Hình {image_count}: {text}\n")
                else:
                    report_lines.append(f"## Hình {image_count}\n")
                
                # Tìm đoạn mô tả tiếp theo (nếu có)
                if i + 1 < len(doc.paragraphs):
                    next_para = doc.paragraphs[i + 1]
                    if next_para.text.strip():
                        report_lines.append(f"\n**Mô tả:** {next_para.text.strip()}\n")
                
                report_lines.append("\n" + "-" * 80 + "\n\n")
        
        # Lưu text của đoạn hiện tại (có thể là caption)
        if text and not any(run._element.xpath('.//a:blip') for run in paragraph.runs):
            current_paragraph_text = text
    
    # Xử lý hình ảnh trong bảng (nếu có)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    text = paragraph.text.strip()
                    if paragraph.runs:
                        for run in paragraph.runs:
                            if run._element.xpath('.//a:blip'):
                                image_count += 1
                                if text:
                                    report_lines.append(f"## Hình {image_count}: {text}\n")
                                else:
                                    report_lines.append(f"## Hình {image_count}\n")
                                report_lines.append("\n" + "-" * 80 + "\n\n")
    
    # Nếu không tìm thấy hình ảnh theo cách trên, thử cách khác
    if image_count == 0:
        print("⚠️ Không tìm thấy hình ảnh bằng cách thông thường, đang thử cách khác...")
        
        # Đếm số hình ảnh trong document
        image_elements = doc.part.related_parts
        print(f"📊 Tổng số phần liên quan: {len(image_elements)}")
        
        # Duyệt lại và tìm các đoạn có thể chứa mô tả hình ảnh
        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if text:
                # Kiểm tra xem có phải là caption không (thường có "Hình", "Figure", "Ảnh", v.v.)
                if any(keyword in text.lower() for keyword in ['hình', 'figure', 'ảnh', 'image', 'biểu đồ', 'chart', 'graph']):
                    image_count += 1
                    report_lines.append(f"## {text}\n")
                    
                    # Tìm đoạn mô tả tiếp theo
                    if i + 1 < len(doc.paragraphs):
                        next_para = doc.paragraphs[i + 1]
                        if next_para.text.strip():
                            report_lines.append(f"\n**Mô tả:** {next_para.text.strip()}\n")
                    
                    report_lines.append("\n" + "-" * 80 + "\n\n")
    
    # Lưu file báo cáo
    if output_path is None:
        docx_file = Path(docx_path)
        output_path = docx_file.parent / f"{docx_file.stem}_report.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report_lines))
    
    print(f"✅ Đã tạo báo cáo: {output_path}")
    print(f"📊 Tổng số hình ảnh đã xử lý: {image_count}")
    
    return output_path

if __name__ == "__main__":
    # Đường dẫn file Word
    docx_path = "report/thuc_hanh.docx"
    
    if not os.path.exists(docx_path):
        print(f"❌ Không tìm thấy file: {docx_path}")
        exit(1)
    
    # Tạo báo cáo
    output_path = read_docx_and_create_report(docx_path)
    print(f"\n✅ Hoàn thành! File báo cáo đã được lưu tại: {output_path}")


