import requests
import json
import psycopg2
from datetime import datetime
import openai
import os
import sys

# Windows 환경에서 유니코드 출력을 위한 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def safe_print(text):
    """안전한 출력 함수 - 유니코드 문자 처리"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 문제가 되는 유니코드 문자를 안전한 문자로 대체
        safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
        print(safe_text)

def search_searxng(query):
    """
    SearxNG API를 사용하여 검색을 수행하는 함수
    """
    # SearxNG API URL (로컬 도커 환경에서 실행 중인 주소)
    url = "http://localhost:4000/search"
    
    # 검색 매개변수 설정 (테스트 결과를 바탕으로 수정)
    params = {
        'q': query,            # 검색어
        'format': 'json'       # 응답 형식 (기본 매개변수만 사용)
        # 'language': 'ko',    # 제거 - 지원되지 않을 수 있음
        # 'time_range': 'day', # 제거 - 지원되지 않을 수 있음
        # 'pageno': 1          # 제거 - 기본값 사용
    }
    
    try:
        # API 요청 보내기
        response = requests.get(url, params=params, timeout=10)
        
        # 요청이 성공했는지 확인
        if response.status_code == 200:
            return response.json()
        else:
            safe_print(f"오류 발생: HTTP 상태 코드 {response.status_code}")
            safe_print(f"응답 내용: {response.text[:200]}...")
            return None
    except Exception as e:
        safe_print(f"요청 중 오류 발생: {e}")
        return None

def display_results(results):
    """
    검색 결과를 보기 좋게 출력하는 함수
    """
    if not results:
        safe_print("검색 결과를 가져올 수 없습니다.")
        return
    
    safe_print(f"\n검색어: {results.get('query')}")
    safe_print(f"검색 결과 수: {results.get('number_of_results', 0)}")
    
    # 검색 제안어 출력
    if 'suggestions' in results and results['suggestions']:
        safe_print("\n관련 검색어:")
        for suggestion in results['suggestions']:
            safe_print(f"  - {suggestion}")
    
    # 검색 결과 출력
    if 'results' in results and results['results']:
        safe_print("\n검색 결과:")
        for i, result in enumerate(results['results'], 1):
            safe_print(f"\n{i}. {result.get('title')}")
            safe_print(f"   URL: {result.get('url')}")
            safe_print(f"   검색 엔진: {', '.join(result.get('engines', []))}")
            
            # 내용이 너무 길면 1000자까지만 표시
            content = result.get('content', '')
            if len(content) > 1000:
                content = content[:1000] + "..."
            
            # 유니코드 문자 안전 처리
            try:
                safe_print(f"   내용: {content}")
            except Exception as e:
                safe_print(f"   내용: [내용 표시 오류: {str(e)}]")
            
            # 최대 10개 결과만 표시
            if i >= 10:
                safe_print(f"\n... 그리고 {len(results['results']) - 10}개 더")
                break
    else:
        safe_print("\n검색 결과가 없습니다.")

# DB 저장 함수 추가
def save_to_db(results, app_name, date):
    conn = psycopg2.connect(
        host="localhost",
        dbname="mydb",
        user="nykim",
        password="1234",
        port=5432
    )
    cur = conn.cursor()
    # 주요 필드 테이블 생성 (app_name, date, answer 컬럼 추가, score/category 제거)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results (
        id SERIAL PRIMARY KEY,
        app_name TEXT,
        quiz_date TEXT,
        title TEXT,
        url TEXT,
        engines TEXT,
        content TEXT,
        published_date DATE,
        answer TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    # 원본 JSON 테이블 생성
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quiz_results_json (
        id SERIAL PRIMARY KEY,
        data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    insert_count = 0
    for result in results.get('results', []):
        # 원본 JSON 저장 (항상)
        cur.execute(
            "INSERT INTO quiz_results_json (data) VALUES (%s)",
            (json.dumps(result, ensure_ascii=False),)
        )
        # 조건에 맞는 경우만 주요 필드 저장 (조건 완화)
        url = result.get('url', '')
        title = result.get('title', '')
        content = result.get('content', '')
        
        # 조건 완화: app_name이 제목에 있거나 내용에 있고, 정답 관련 키워드가 있으면 저장
        if isinstance(date, str):
            date_str_1 = date
            date_str_2 = date
        elif hasattr(date, 'strftime'):
            # 두 가지 형식으로 변환: 07월 06일, 7월 6일
            date_str_1 = date.strftime('%m월 %d일')  # 07월 06일
            # 7월 6일 형식으로 변환 (앞의 0 제거)
            month = str(date.month)  # 7
            day = str(date.day)      # 6
            date_str_2 = f"{month}월 {day}일"  # 7월 6일
        else:
            date_str_1 = str(date) if date else ""
            date_str_2 = str(date) if date else ""
            
        if (
            (app_name in title or app_name in content) and
            (date_str_1 in title or date_str_2 in title or date_str_1 in content or date_str_2 in content) and
            ("정답" in content or "답" in content or "퀴즈" in title)
        ):
            # LLM에게 정답 추출 요청
            answer = extract_answer_with_llm(content, app_name, date_str_1)
            safe_print(f"[LLM 정답 추출] {answer}")
            cur.execute(
                """
                INSERT INTO quiz_results (app_name, quiz_date, title, url, engines, content, published_date, answer)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    app_name,
                    date_str_1,
                    title,
                    url,
                    ','.join(result.get('engines', [])),
                    content,
                    result.get('publishedDate'),
                    answer
                )
            )
            safe_print(f"[INSERT] title: {title}\n         url: {url}")
            insert_count += 1
    conn.commit()
    cur.close()
    conn.close()
    safe_print(f"DB 저장 완료! (quiz_results에 {insert_count}건 저장)")

def extract_answer_with_llm(content, app_name, quiz_date):
    #openai.api_key = os.getenv('OPENAI_API_KEY')
    openai.api_key = "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"   
    
    prompt = f"""아래 텍스트에서 퀴즈의 정답만 뽑아서 알려줘.
    {content}
    
    강력한 정답 추출 규칙:
    1. 가장 짧고 핵심적인 답만 선택해줘 (긴 문장 절대 금지!)
    2. 단어 하나 또는 최대 2-3단어 조합만 허용
    3. "○○○○○" 빈칸이 있는 문장에서는 그 빈칸에 들어갈 단어만 찾아줘. ooooo를 포함한 문장은 노출 절대 금지!
    4. 브랜드명, 제품명, 인물명 등 고유명사 우선
    5. 설명문, 광고문구, 긴 문장은 절대 선택하지 마
    6. 특수문자(따옴표, 괄호 등)로 묶인 핵심 단어가 있으면 그것을 우선 추출
    7. 여러 후보 중 가장 간단하고 명확한 답 선택
    
    예시:
    - "올리브영 1등 질 유산균 ○○○○○!" → 제품명만 추출 (예: 락토핏)
    - "미국 연극·뮤지컬계의 가장 권위 있는 상" → 상 이름만 추출 (예: 토니상)

    최종 정답 (단어만):"""
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "너는 퀴즈 정답 추출 전문가야. 반드시 가장 짧고 핵심적인 단어만 추출해야 해. 긴 문장, 설명문, 광고문구는 절대 정답이 아니야. 오직 핵심 단어(고유명사, 브랜드명, 제품명 등)만 추출해줘. 예: '락토핏', '토니상', '김치' 같은 단순한 답만 허용해."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=20,
        temperature=0
    )
    answer = response.choices[0].message.content.strip()
    return answer

# 메인 함수
def main():
    # quiz_list 테이블에서 app_name과 date 가져오기
    conn = psycopg2.connect(
        host="localhost",
        dbname="mydb",
        user="nykim",
        password="1234",
        port=5432
    )
    cur = conn.cursor()
    
    # quiz_list 테이블에서 app_name과 date 조회
    cur.execute("""
        SELECT DISTINCT app_name, quiz_date 
        FROM quiz_list 
        ORDER BY app_name, quiz_date
    """)
    
    quiz_items = cur.fetchall()
    cur.close()
    conn.close()
    
    if not quiz_items:
        safe_print("quiz_list 테이블에 데이터가 없습니다.")
        return
    
    safe_print(f"총 {len(quiz_items)}개의 퀴즈 항목을 검색합니다...")
    
    for app_name, date in quiz_items:
        safe_print(f"\n{'='*50}")
        safe_print(f"검색 중: {app_name} - {date}")
        safe_print(f"{'='*50}")
        
        # 다양한 검색 쿼리로 시도
        queries = [
            f"{app_name} 오늘의 퀴즈 {date} 정답",
            f"{app_name} 퀴즈 {date} 답",
            f"{app_name} {date} 정답 공개",
            f"{app_name} 오늘의 퀴즈 정답 {date}",
            f'"{app_name}" "{date}" 정답'
        ]
        
        all_results = []
        
        for query in queries:
            safe_print(f"검색어: '{query}'")
            
            results = search_searxng(query)
            
            if results and results.get('results'):
                all_results.extend(results.get('results', []))
                safe_print(f"   → {len(results.get('results', []))}개 결과 수집")
            else:
                safe_print("   → 검색 결과 없음")
        
        # 중복 제거 (URL 기준)
        unique_results = {}
        for result in all_results:
            url = result.get('url', '')
            if url not in unique_results:
                unique_results[url] = result
        
        final_results = list(unique_results.values())
        
        if final_results:
            # 결과를 보기 좋게 출력
            combined_results = {
                'query': f"{app_name} {date} 정답 검색",
                'results': final_results,
                'number_of_results': len(final_results)
            }
            display_results(combined_results)
            
            # 통계 정보 출력
            safe_print(f"\n📊 검색 통계:")
            safe_print(f"   - 총 결과 수: {len(final_results)}")
            safe_print(f"   - 검색 쿼리 수: {len(queries)}")
            
            # DB 저장
            save_to_db(combined_results, app_name, date)
        else:
            safe_print("모든 검색에서 결과를 찾을 수 없습니다.")
        
        safe_print(f"\n{app_name} - {date} 검색 완료\n")

if __name__ == "__main__":
    main() 