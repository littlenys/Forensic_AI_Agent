from services.planner_service import run_full_planning
from pipelines.input_pipeline import preprocess_input
from pipelines.result_pipeline import postprocess_result
import os
import json
from flask import Flask, request, jsonify
import threading


if __name__ == "__main__":    
    user_input = """Phân tích file trong đường dẫn: E:/Task/202507_SOC_Forensic/code/test/test_environment/8651_csm_cms.access.log 
    Bước 1: Đọc 3 dòng đầu tiên để lấy format
    Bước 2: Viết code python để chuyển dữ liệu từ file log về csv và lưu lại 
    """
    print(user_input)
    processed_input = preprocess_input(user_input)
    result, trace = run_full_planning(processed_input)

#    app.run(debug=True, host='0.0.0.0', port=9999)