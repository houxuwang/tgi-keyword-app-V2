from flask import Flask, request, render_template, send_file
import pandas as pd
import numpy as np
from io import BytesIO
from tgi_module import generate_tgi_dual_outputs_to_excel

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/generate_tags", methods=["POST"])
def generate_tags():
    try:
        file = request.files["file"]
        df = pd.read_excel(file)

        # ✅ 添加空值检查（第 0 和 1 列）
        if df.iloc[:, 0].isnull().any() or df.iloc[:, 1].isnull().any():
            return "<h3>标签类型或标签有空值，请检查上传的数据表</h3>"

        params = request.form
        threshold = float(params.get("threshold", "nan"))
        tgi_threshold = float(params.get("tgi_threshold", "nan"))
        share_threshold = float(params.get("share_threshold", "nan"))

        # 调用你封装的函数（返回标签表 + TGI原始表）
        combined_df, df_with_tgi = generate_tgi_dual_outputs_to_excel(
            df=df,
            threshold=threshold,
            tgi_threshold=tgi_threshold,
            share_threshold=share_threshold
        )

        # 构建 Excel 输出文件流
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            combined_df.to_excel(writer, sheet_name="TGI标签输出")
            df_with_tgi.to_excel(writer, sheet_name="原始数据含TGI", index=True)
        output.seek(0)
        
        filename = f"标签输出_T{threshold}_TGI{tgi_threshold}_SHARE{share_threshold}.xlsx"
        return send_file(output, download_name=filename, as_attachment=True)
        

    except Exception as e:
        return f"<h3>出错了: {str(e)}</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)