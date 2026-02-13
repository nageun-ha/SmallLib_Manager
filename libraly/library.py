import csv
import os
from datetime import datetime, timedelta
import cv2
import sys
import ctypes.util


# macOS에서 zbar 공유 라이브러리를 찾지 못하는 문제를 해결하기 위한 패치 코드
if sys.platform == 'darwin':
    _original_find_library = ctypes.util.find_library
    def _find_library_patched(name):
        if name == 'zbar':

            candidates = [
                '/opt/homebrew/lib/libzbar.dylib',
                '/usr/local/lib/libzbar.dylib'
            ]
            for path in candidates:
                if os.path.exists(path):
                    return path
        return _original_find_library(name)
    ctypes.util.find_library = _find_library_patched

from pyzbar.pyzbar import decode

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_FILE = os.path.join(SCRIPT_DIR, 'books.csv')

# CSV 파일 로드
def load():
    books = []
    if not os.path.exists(BOOKS_FILE):
        return books
    with open(BOOKS_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            books.append(row)
    return books

# CSV 파일 저장
def save(books):
    with open(BOOKS_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'title', 'author', 'available', 'borrower', 'due_date']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for b in books:
            writer.writerow(b)

# 도서 등록
def register_book():
    books = load()
    # 기존 도서가 있으면 마지막 ID에 1을 더하고, 없으면 1번부터 시작
    new_id = str(int(books[-1]['id']) + 1) if books else '1'
    title = input("제목: ")
    author = input("저자: ")
    books.append({'id': new_id, 'title': title, 'author': author, 'available': 'yes', 'borrower': '', 'due_date': ''})
    save(books)
    print("도서 등록 완료")

# 도서 목록 출력
def list_books():
    books = load()
    today = datetime.now().date()
    for b in books:
        if b['available'] == 'yes':
            status = '대출가능'
        else:
            try:
                # 반납 예정일(due_date) 문자열을 날짜 객체로 변환하여 오늘 날짜와 비교
                due = datetime.strptime(b['due_date'], '%Y-%m-%d').date()
                if due < today:
                    status = f"연체됨({b['borrower']})"
                else:
                    status = f"대출중({b['borrower']})"
            except:
                # 변환 실패 시(데이터 오류 등) '대출중'으로만 표시하고 넘어감
                status = f"대출중({b['borrower']})"
        print(f"{b['id']} | {b['title']} | {b['author']} | {status}")

# 도서 검색
def search_books():
    keyword = input("검색할 제목 또는 저자: ")
    books = load()
    for b in books:
        if keyword in b['title'] or keyword in b['author']:
            print(f"{b['id']} | {b['title']} | {b['author']} | {'대출가능' if b['available']=='yes' else '대출중'}")

# 바코드 인식
def scan_barcode():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("카메라가 연결되어 있지 않습니다.")
        return None

    barcode_data = None
    print("바코드를 스캔하세요. 취소하려면 ESC를 누르세요.")
    while True:
        # 카메라 프레임을 계속 읽어오며 바코드가 인식되면 데이터 반환
        ret, frame = cap.read()
        if not ret:
            break
        for code in decode(frame):
            barcode_data = code.data.decode('utf-8')
            cap.release()
            cv2.destroyAllWindows()
            return barcode_data
        cv2.imshow("Barcode Scanner", frame)
        # ESC 키(ASCII 27)를 누르면 스캔 중단
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    cap.release()
    cv2.destroyAllWindows()
    return None

# 도서 대출
def borrow_book():
    books = load()
    book_id = scan_barcode()

    if not book_id:
        book_id = input("바코드 인식 실패. 도서 ID를 수동 입력하세요: ")

    for b in books:
        if str(b['id']).strip() == str(book_id).strip():
            if b['available'] == 'no':
                print("이미 대출 중인 도서입니다.")
                return
            b['available'] = 'no'
            b['borrower'] = input("대출자 이름: ")
            # 대출 기간은 2주(14일)로 설정
            b['due_date'] = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
            save(books)
            print("도서 대출 완료")
            return
    print("해당 도서 ID를 찾을 수 없습니다.")

# 도서 반납
def return_book():
    books = load()
    book_id = scan_barcode()

    if not book_id:
        book_id = input("바코드 인식 실패. 도서 ID를 수동 입력하세요: ")
    for b in books:
        if str(b['id']).strip() == str(book_id).strip():
            if b['available'] == 'yes':
                print("이미 반납된 도서입니다.")
                return
            b['available'] = 'yes'
            b['borrower'] = ''
            b['due_date'] = ''
            save(books)
            print("도서 반납 완료")
            return
    print("해당 도서 ID를 찾을 수 없습니다.")

# 연체 도서 확인
def check_overdue_books():
    books = load()
    today = datetime.now().date()
    found = False
    for b in books:
        if b['available'] == 'no' and b['due_date']:
            try:
                due = datetime.strptime(b['due_date'], '%Y-%m-%d').date()
                if due < today:
                    print(f"연체 도서: {b['id']} | {b['title']} | {b['author']} | 대출자: {b['borrower']} | 반납기한: {b['due_date']}")
                    found = True
            except ValueError:
                print(f"날짜 형식 오류: {b['id']} | {b['due_date']}")
    if not found:
        print("연체된 도서가 없습니다.")

# 프로그램 메인 메뉴
def main():
    while True:
        print("\n1. 도서 목록\n2. 도서 등록\n3. 도서 검색\n4. 도서 대출\n5. 도서 반납\n6. 연체 도서 확인\n7. 종료")
        choice = input("선택: ")
        if choice == '1':
            list_books()
        elif choice == '2':
            register_book()
        elif choice == '3':
            search_books()
        elif choice == '4':
            borrow_book()
        elif choice == '5':
            return_book()
        elif choice == '6':
            check_overdue_books()
        elif choice == '7':
            break
        else:
            print("잘못된 입력입니다.")

if __name__ == '__main__':
    main()
