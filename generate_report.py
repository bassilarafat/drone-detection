from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import csv
import datetime

# ── helpers ──────────────────────────────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_col_width(table, col_idx, width_cm):
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)

def add_header_row(table, headers, bg='1F3864'):
    row = table.rows[0]
    for i, h in enumerate(headers):
        cell = row.cells[i]
        cell.text = h
        set_cell_bg(cell, bg)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)

def add_data_row(table, values, row_idx, shade_color='DCE6F1'):
    row = table.add_row()
    for i, v in enumerate(values):
        cell = row.cells[i]
        cell.text = str(v)
        if row_idx % 2 == 0:
            set_cell_bg(cell, shade_color)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.runs[0]
        run.font.size = Pt(10)
    return row

def add_section_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.runs[0].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    return p

def add_kv_table(doc, rows):
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    add_header_row(table, ['Parameter', 'Value'])
    for i, (k, v) in enumerate(rows):
        r = table.add_row()
        r.cells[0].text = k
        r.cells[1].text = v
        if i % 2 == 0:
            set_cell_bg(r.cells[0], 'DCE6F1')
            set_cell_bg(r.cells[1], 'DCE6F1')
        for cell in r.cells:
            cell.paragraphs[0].runs[0].font.size = Pt(10)
    set_col_width(table, 0, 7)
    set_col_width(table, 1, 7)
    doc.add_paragraph()

# ── load results ──────────────────────────────────────────────────────────────

csv_path = r'runs\detect\runs\anti_uav_yolo11s\results.csv'
epochs_data = []
with open(csv_path, newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        epochs_data.append({k.strip(): v.strip() for k, v in row.items()})

final = epochs_data[-1]
total_epochs = len(epochs_data)
total_time_s = float(final['time'])
total_time_h = total_time_s / 3600

# ── build document ────────────────────────────────────────────────────────────

doc = Document()

# page margins
for section in doc.sections:
    section.top_margin    = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# default font
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

# ── title block ───────────────────────────────────────────────────────────────
title = doc.add_heading('Training Report', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.runs[0].font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
title.runs[0].font.size = Pt(24)

sub = doc.add_paragraph('Anti-UAV Drone Detection Model — YOLOv11s')
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.runs[0].font.size = Pt(13)
sub.runs[0].bold = True
sub.runs[0].font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

date_p = doc.add_paragraph(f'Date: {datetime.date.today().strftime("%B %d, %Y")}')
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
date_p.runs[0].font.size = Pt(10)
date_p.runs[0].font.color.rgb = RGBColor(0x70, 0x70, 0x70)

doc.add_paragraph()

# ── 1. experiment configuration ───────────────────────────────────────────────
add_section_heading(doc, '1. Experiment Configuration')
add_kv_table(doc, [
    ('Base Model',              'YOLOv11s (pretrained on COCO)'),
    ('Task',                    'Object Detection — Single Class (Drone)'),
    ('Input Resolution',        '640 × 640 px'),
    ('Epochs',                  str(total_epochs)),
    ('Batch Size',              '16'),
    ('Optimizer',               'Auto (SGD-based with momentum 0.937)'),
    ('Initial Learning Rate',   '0.01'),
    ('Final Learning Rate',     '0.01'),
    ('Warmup Epochs',           '3'),
    ('Mixed Precision (AMP)',   'Enabled'),
    ('Hardware',                'GPU (CUDA device 0)'),
    ('Total Training Time',     f'{total_time_h:.2f} hours ({total_time_s/60:.0f} min)'),
])

# ── 2. dataset ────────────────────────────────────────────────────────────────
add_section_heading(doc, '2. Dataset')
add_kv_table(doc, [
    ('Dataset',         'Anti-UAV RGBT Benchmark'),
    ('Classes',         '1 — drone'),
    ('Training Images', '26,439'),
    ('Validation Images','5,831'),
    ('Total Images',    '32,270'),
])

aug = doc.add_paragraph()
aug.add_run('Augmentation strategy (tuned for small objects): ').bold = True
doc.add_paragraph('• Mosaic augmentation enabled; disabled for last 5 epochs (close_mosaic=5)', style='List Bullet')
doc.add_paragraph('• Random scale ±50%', style='List Bullet')
doc.add_paragraph('• Horizontal flip probability 50%', style='List Bullet')
doc.add_paragraph('• Random erasing 40%', style='List Bullet')
doc.add_paragraph('• RandAugment enabled', style='List Bullet')
doc.add_paragraph()

# ── 3. final performance ──────────────────────────────────────────────────────
add_section_heading(doc, '3. Final Performance (Epoch 30)')

table = doc.add_table(rows=1, cols=2)
table.style = 'Table Grid'
table.alignment = WD_TABLE_ALIGNMENT.CENTER
add_header_row(table, ['Metric', 'Value'])

metrics = [
    ('mAP@50',        f"{float(final['metrics/mAP50(B)'])*100:.1f}%"),
    ('mAP@50-95',     f"{float(final['metrics/mAP50-95(B)'])*100:.1f}%"),
    ('Precision',     f"{float(final['metrics/precision(B)'])*100:.1f}%"),
    ('Recall',        f"{float(final['metrics/recall(B)'])*100:.1f}%"),
    ('Val Box Loss',  f"{float(final['val/box_loss']):.4f}"),
    ('Val Cls Loss',  f"{float(final['val/cls_loss']):.4f}"),
    ('Val DFL Loss',  f"{float(final['val/dfl_loss']):.4f}"),
]
for i, (k, v) in enumerate(metrics):
    r = table.add_row()
    r.cells[0].text = k
    r.cells[1].text = v
    if i % 2 == 0:
        set_cell_bg(r.cells[0], 'DCE6F1')
        set_cell_bg(r.cells[1], 'DCE6F1')
    # bold the top 4 key metrics
    if i < 4:
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[1].paragraphs[0].runs[0].bold = True
    for cell in r.cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cell.paragraphs[0].runs[0].font.size = Pt(10)

set_col_width(table, 0, 7)
set_col_width(table, 1, 7)
doc.add_paragraph()

# ── 4. training progression ───────────────────────────────────────────────────
add_section_heading(doc, '4. Training Progression')

prog_table = doc.add_table(rows=1, cols=5)
prog_table.style = 'Table Grid'
prog_table.alignment = WD_TABLE_ALIGNMENT.CENTER
add_header_row(prog_table, ['Epoch', 'mAP@50', 'mAP@50-95', 'Precision', 'Recall'])

selected = [0, 4, 9, 14, 19, 24, 29]  # 0-based indices = epochs 1,5,10,15,20,25,30
for row_i, idx in enumerate(selected):
    d = epochs_data[idx]
    add_data_row(prog_table, [
        int(float(d['epoch'])),
        f"{float(d['metrics/mAP50(B)'])*100:.1f}%",
        f"{float(d['metrics/mAP50-95(B)'])*100:.1f}%",
        f"{float(d['metrics/precision(B)'])*100:.1f}%",
        f"{float(d['metrics/recall(B)'])*100:.1f}%",
    ], row_i)

doc.add_paragraph()

# ── 5. loss convergence ───────────────────────────────────────────────────────
add_section_heading(doc, '5. Loss Convergence')

loss_table = doc.add_table(rows=1, cols=4)
loss_table.style = 'Table Grid'
loss_table.alignment = WD_TABLE_ALIGNMENT.CENTER
add_header_row(loss_table, ['Epoch', 'Train Box Loss', 'Val Box Loss', 'Train Cls Loss'])

for row_i, idx in enumerate(selected):
    d = epochs_data[idx]
    add_data_row(loss_table, [
        int(float(d['epoch'])),
        f"{float(d['train/box_loss']):.4f}",
        f"{float(d['val/box_loss']):.4f}",
        f"{float(d['train/cls_loss']):.4f}",
    ], row_i)

doc.add_paragraph()
note = doc.add_paragraph()
note.add_run('Observation: ').bold = True
note.add_run(
    'Training and validation losses decreased steadily across all 30 epochs with no sign of overfitting. '
    'The close tracking between training and validation loss curves indicates strong generalisation.'
)
doc.add_paragraph()

# ── 6. output artifacts ───────────────────────────────────────────────────────
add_section_heading(doc, '6. Output Artifacts')
add_kv_table(doc, [
    ('weights/best.pt',              'Best checkpoint — highest mAP@50-95 (epoch 26)'),
    ('weights/last.pt',              'Final epoch checkpoint'),
    ('results.csv',                  'Full per-epoch metrics log'),
    ('results.png',                  'Training curves (losses + metrics)'),
    ('confusion_matrix.png',         'Confusion matrix on validation set'),
    ('confusion_matrix_normalized.png', 'Normalised confusion matrix'),
    ('BoxPR_curve.png',              'Precision-Recall curve'),
    ('BoxF1_curve.png',              'F1-confidence curve'),
    ('val_batch*_pred.jpg',          'Sample validation predictions (3 batches)'),
])

# ── 7. summary ────────────────────────────────────────────────────────────────
add_section_heading(doc, '7. Summary & Next Steps')

summary = (
    'The YOLOv11s model was successfully fine-tuned on the Anti-UAV RGBT benchmark for single-class '
    'drone detection. After 30 epochs the model achieved 99.4% mAP@50 and 68.1% mAP@50-95, with '
    'precision and recall both exceeding 99%. Training converged cleanly with no overfitting observed. '
    'The model is ready for evaluation on the held-out test set and subsequent deployment or further ablation studies.'
)
doc.add_paragraph(summary)

doc.add_paragraph()
next_p = doc.add_paragraph()
next_p.add_run('Suggested next steps:').bold = True
for step in [
    'Run inference on the held-out test set to obtain final test-set metrics.',
    'Export best.pt to ONNX / TensorRT for deployment.',
    'Conduct ablation study comparing YOLOv11s vs larger variants (YOLOv11m/l).',
    'Evaluate model robustness on infrared-only frames from the RGBT dataset.',
]:
    doc.add_paragraph(step, style='List Bullet')

# ── save ──────────────────────────────────────────────────────────────────────
out = r'Training_Report_AntiUAV_YOLOv11s.docx'
doc.save(out)
print(f'Saved: {out}')
