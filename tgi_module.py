# tgi_module.py

import pandas as pd
import numpy as np

def generate_tgi_dual_outputs_to_excel(
    df,
    threshold,
    tgi_threshold,
    share_threshold
):
    label_col = df.columns[0]
    tag_col = df.columns[1]
    base_column = df.columns[2]
    seg_names = df.columns[3:].tolist()
    tgi_names = [f"TGI_{col}" for col in seg_names]

    df[base_column] = pd.to_numeric(df[base_column], errors='coerce')
    for seg_col, tgi_col in zip(seg_names, tgi_names):
        df[seg_col] = pd.to_numeric(df[seg_col], errors='coerce')
        df[tgi_col] = df[seg_col] / df[base_column] * 100

    label_types = df[label_col].dropna().unique().tolist()

    output1 = pd.DataFrame(index=label_types, columns=seg_names)
    if not pd.isna(threshold):
        for seg in seg_names:
            df_seg = df[df[seg] > threshold]
            for label_type in label_types:
                tags = df_seg[df_seg[label_col] == label_type][tag_col].dropna().astype(str).tolist()
                output1.loc[label_type, seg] = ", ".join(tags) if tags else ""
    output1.fillna("", inplace=True)

    output2 = pd.DataFrame(index=label_types, columns=seg_names)
    if not (pd.isna(tgi_threshold) and pd.isna(share_threshold)):
        for seg_col, tgi_col in zip(seg_names, tgi_names):
            df_seg = df.copy()
            conditions = []
            if not pd.isna(tgi_threshold):
                conditions.append(df_seg[tgi_col] >= tgi_threshold)
            if not pd.isna(share_threshold):
                conditions.append(df_seg[base_column] > share_threshold)
            if conditions:
                combined_mask = np.logical_and.reduce(conditions)
                df_seg = df_seg[combined_mask]
            for label_type in label_types:
                tags = df_seg[df_seg[label_col] == label_type][tag_col].dropna().astype(str).tolist()
                output2.loc[label_type, seg_col] = ", ".join(tags) if tags else ""
    output2.fillna("", inplace=True)

    def merge_cells(x, y):
        parts = []
        for v in [x, y]:
            if pd.notna(v) and v != "":
                parts.extend([i.strip() for i in str(v).split(",") if i.strip()])
        return ", ".join(sorted(set(parts)))

    combined = pd.DataFrame(index=label_types, columns=seg_names)
    for row in label_types:
        for col in seg_names:
            combined.loc[row, col] = merge_cells(output1.loc[row, col], output2.loc[row, col])

    combined = combined.fillna("")
    return combined, df  # 返回两个表