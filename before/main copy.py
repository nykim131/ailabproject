from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

def load_quiz_data():
    """quiz.json 파일에서 퀴즈 데이터를 로드합니다."""
    try:
        with open('quiz.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print("quiz.json 파일을 찾을 수 없습니다.")
        return {"results": [], "query": "", "number_of_results": 0}
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        return {"results": [], "query": "", "number_of_results": 0}

@app.route('/')
def index():
    """메인 페이지 - 돈버는 퀴즈 앱"""
    quiz_data = load_quiz_data()
    return render_template('index.html', quiz_data=quiz_data)

@app.route('/api/quiz')
def api_quiz():
    """퀴즈 데이터 API 엔드포인트"""
    quiz_data = load_quiz_data()
    return jsonify(quiz_data)

@app.route('/api/quiz/<int:quiz_id>')
def api_quiz_detail(quiz_id):
    """특정 퀴즈 상세 정보 API"""
    quiz_data = load_quiz_data()
    if 0 <= quiz_id < len(quiz_data.get('results', [])):
        return jsonify(quiz_data['results'][quiz_id])
    return jsonify({"error": "퀴즈를 찾을 수 없습니다."}), 404

@app.route('/api/stats')
def api_stats():
    """퀴즈 통계 API"""
    quiz_data = load_quiz_data()
    results = quiz_data.get('results', [])
    
    if not results:
        return jsonify({
            "total_quizzes": 0,
            "average_score": 0,
            "latest_update": None,
            "engines": []
        })
    
    # 통계 계산
    total_quizzes = len(results)
    average_score = sum(result.get('score', 0) for result in results) / total_quizzes
    
    # 최신 업데이트 날짜
    latest_update = None
    for result in results:
        if result.get('publishedDate'):
            try:
                date = datetime.strptime(result['publishedDate'], '%Y-%m-%d')
                if latest_update is None or date > latest_update:
                    latest_update = date
            except ValueError:
                continue
    
    # 사용된 엔진들
    engines = list(set(result.get('engine', '') for result in results if result.get('engine')))
    
    return jsonify({
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2),
        "latest_update": latest_update.strftime('%Y-%m-%d') if latest_update else None,
        "engines": engines
    })

@app.route('/api/search')
def api_search():
    """퀴즈 검색 API"""
    query = request.args.get('q', '').lower()
    quiz_data = load_quiz_data()
    results = quiz_data.get('results', [])
    
    if not query:
        return jsonify(results)
    
    # 검색 필터링
    filtered_results = []
    for result in results:
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        
        if query in title or query in content:
            filtered_results.append(result)
    
    return jsonify(filtered_results)

@app.route('/api/filter')
def api_filter():
    """퀴즈 필터링 API"""
    engine = request.args.get('engine', 'all')
    quiz_data = load_quiz_data()
    results = quiz_data.get('results', [])
    
    if engine == 'all':
        return jsonify(results)
    
    # 엔진별 필터링
    filtered_results = [result for result in results if result.get('engine') == engine]
    return jsonify(filtered_results)

@app.route('/api/sort')
def api_sort():
    """퀴즈 정렬 API"""
    order = request.args.get('order', 'desc')  # desc 또는 asc
    quiz_data = load_quiz_data()
    results = quiz_data.get('results', [])
    
    # 점수별 정렬
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=(order == 'desc'))
    return jsonify(sorted_results)

@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.errorhandler(404)
def not_found(error):
    """404 에러 핸들러"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 에러 핸들러"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    # 개발 환경에서 디버그 모드 활성화
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 돈버는 퀴즈 앱이 시작됩니다...")
    print("📍 접속 주소: http://localhost:5000")
    print("📊 API 문서: http://localhost:5000/api/quiz")
    print("💡 개발 모드:", debug_mode)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        threaded=True
    ) 