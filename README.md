# Mart-Compare 프로젝트 분석 보고서

## 작업 환경

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Mart Compare (편의점 행사상품 비교 서비스) |
| **OS** | Windows (WSL2 Ubuntu) |
| **프론트엔드** | React 19 + TypeScript 6 + Vite 8 |
| **백엔드** | Spring Boot 3.5 + Java 17 + Gradle |
| **DB** | MySQL 8 (로컬: `mart_compare`) |
| **크롤러** | Python 3 + Selenium + Pandas |
| **지도 API** | Kakao Maps API |
| **IDE** | IntelliJ IDEA (`.idea/` 존재) |
| **포트 구성** | Backend `8081`, Frontend `5173` (Vite dev server) |
| **Git 커밋 수** | 5개 (초기 세팅 ~ 카카오맵 마커 추가) |

---

## 1. 어떤 사이트인가?

**CU 편의점의 1+1 / 2+1 행사상품을 지도 위에서 조회할 수 있는 웹 애플리케이션**이다.

- CU 홈페이지에 올라오는 행사상품 정보를 **자동 수집(크롤링)** 하여 DB에 저장
- 저장된 상품을 **Spring Boot REST API**로 제공
- React 프론트엔드에서 **카카오 지도**와 함께 **상품 리스트**를 표시
- 향후 GS25, 세븐일레븐 등 여러 편의점을 추가하여 **가격/행사 비교**까지 확장 가능한 구조

---

## 2. 주요 기능

### 2.1 CU 행사상품 크롤링 (`crawler/cu_crawler.py`)
- Selenium WebDriver로 CU 이벤트 페이지(`cu.bgfretail.com/event/plus.do`) 접속
- **1+1** 탭과 **2+1** 탭의 상품명, 가격, 행사종류를 수집
- 결과를 `cu_products.csv`로 저장 (utf-8-sig 인코딩)

### 2.2 CSV → DB 적재 (`crawler/db_insert.py`)
- PyMySQL로 MySQL `mart_compare` DB에 접속
- CSV에서 읽은 데이터를 `product` 테이블에 `mart_id=1 (CU)`로 INSERT

### 2.3 REST API (`backend`)
| 계층 | 파일 | 역할 |
|------|------|------|
| Entity | `Product.java` | `product` 테이블과 매핑되는 JPA 엔티티 |
| Repository | `ProductRepository.java` | JpaRepository 상속, 기본 CRUD 제공 |
| Service | `ProductService.java` | 전체 상품 조회 비즈니스 로직 |
| Controller | `ProductController.java` | `GET /api/products` 엔드포인트 |
| Config | `CorsConfig.java` | `localhost:5173`에서 오는 CORS 허용 |

### 2.4 프론트엔드 (`frontend`)
- **카카오맵 표시**: Kakao Maps SDK를 동적 `<script>` 로딩, 서울시청 기준 마커 표시
- **상품 리스트**: `localhost:8081/api/products`에서 받아온 데이터를 우측 패널에 렌더링
- 마커 클릭 시 인포윈도우로 매장명 표시

### 2.5 DB 스키마 (`mysql/`)
```sql
mart (id, name, address, latitude, longitude)
product (id, mart_id FK, name, price, event_type)
```

---

## 3. 기술 선택 이유 및 아키텍처

### 3.1 Python Selenium 크롤러
- **선택 이유**: CU 사이트는 JavaScript로 동적 렌더링되는 SPA 형태. 단순 HTTP GET으로는 상품 데이터를 가져올 수 없어 **실제 브라우저를 구동하는 Selenium** 선택
- **대안**: `requests` + BeautifulSoup → JS 렌더링 불가로 탈락. `Playwright`도 가능했지만 팀에 Selenium 경험자가 있어 채택

### 3.2 Spring Boot + JPA
- **선택 이유**: 팀의 주력 백엔드 스택. MyBatis 대신 JPA를 선택한 것은 단순 CRUD 위주라 ORM의 이점(생산성, 유지보수)이 더 크다고 판단
- `ddl-auto=none`으로 설정한 이유: **테이블은 SQL로 직접 생성**하고 JPA는 읽기만 담당 → 운영에서의 예상치 못한 스키마 변경 방지

### 3.3 React + Vite + TypeScript
- **선택 이유**: CRA는 유지보수 중단 수준, Next.js는 SSR이 필요 없는 단순 지도 앱이라 과함. Vite가 가장 가볍고 빠름
- TypeScript는 **Kakao Maps의 window 전역 객체 타입 선언**을 위해 필수적 (`declare global { interface Window { kakao: any } }`)

### 3.4 Kakao Maps API
- **선택 이유**: 국내 지도 API 중 카카오가 점유율 1위, CU 매장 정보와의 연동성이 좋음
- `autoload=false` + `kakao.maps.load()`로 수동 로딩한 이유: **React의 컴포넌트 라이프사이클과 SDK 로딩 타이밍을 정확히 제어**하기 위함

---

## 4. 겪기 쉬운 문제와 해결 방법

### 4.1 Selenium 크롤링: `element not interactable` / `no such element`

**문제**: CU 페이지의 2+1 탭은 `<a>` 태그 클릭이 아닌 `goDepth('24')` JavaScript 함수 호출로 전환된다. `click()`으로는 탭 전환이 안 되는 경우가 많음.

**해결**: `driver.execute_script("goDepth('24')")`로 직접 JS 함수 호출. 이후 `time.sleep(2)`로 렌더링 대기 후 상품 목록 재수집.

```python
# bad: driver.find_element(...).click()
# good:
driver.execute_script("goDepth('24')")
time.sleep(2)
```

### 4.2 Windows vs WSL 경로 문제

**문제**: `db_insert.py`에 하드코딩된 경로 `C:\\projects\\mart-crawler\\cu_products.csv`는 WSL 환경에서 동작하지 않음.

**해결**: WSL 내에서 크롤러를 실행하면 `cu_products.csv`가 현재 디렉터리에 생성되므로, 경로를 `cu_products.csv`로 상대 경로로 바꾸거나 WSL 절대 경로(`/home/...`)로 변경 필요. (현재 코드에는 미반영된 과제)

### 4.3 CORS 에러 (프론트-백엔드 연동)

**문제**: `localhost:5173`에서 `localhost:8081`로 API 호출 시 CORS 정책 위반.

**해결**: Spring Boot에 `CorsConfig`를 추가하여 `/api/**` 패턴에 대해 `localhost:5173` 출처를 명시적으로 허용. `allowedOrigins("*")` 대신 특정 Origin만 허용하여 보안 유지.

```java
registry.addMapping("/api/**")
        .allowedOrigins("http://localhost:5173")
```

### 4.4 Kakao Maps SDK와 React 동기화

**문제**: `<script>` 태그로 Kakao Maps SDK를 로드하는 시점과 React 컴포넌트가 마운트되는 시점이 달라 지도가 렌더링되지 않음.

**해결**:
1. `autoload=false` 파라미터로 SDK 자동 로딩 방지
2. `script.onload` 콜백 내에서 `kakao.maps.load()` 호출
3. `useRef`로 지도 DOM 요소 참조 유지 → null 체크 후 지도 객체 생성

```typescript
script.onload = () => {
  window.kakao.maps.load(() => {
    if (!mapRef.current) return;
    const map = new window.kakao.maps.Map(mapRef.current, options);
  });
};
```

### 4.5 가격 데이터 전처리 (CSV → DB)

**문제**: CSV에서 가격이 `"4,500"` (문자열 + 콤마) 형태로 들어와 DB에 INTEGER 컬럼에 INSERT 불가.

**해결**: `int(str(row["가격"]).replace(",", ""))`로 쉼표 제거 후 정수 변환.

### 4.6 `ddl-auto=none`으로 인한 JPA 테이블 매핑 실수

**문제**: 엔티티 클래스의 `@Column(name = "event_type")`과 실제 DB 컬럼명이 다르면 JPA가 생성하는 쿼리가 달라져 에러 발생.

**해결**: SQL 직접 작성 + `ddl-auto=none` 전략을 유지하며, 엔티티 필드마다 `@Column(name = "...")`로 **명시적 매핑**하여 실수 방지.

---

## 5. 향후 개선 방향 (코드 상의 TODO)

1. **멀티 편의점 지원**: `mart` 테이블에 GS25, 세븐일레븐 추가 → 각 편의점별 크롤러 작성 필요
2. **크롤러 중복 제거**: `cu_crawler.py`의 패턴을 추상화하여 편의점별 크롤러 클래스로 리팩터링
3. **에러 핸들링 개선**: 현재 크롤러의 `try/except` pass 패턴 → 로깅 및 재시도 로직 필요
4. **지도 마커 동적 표시**: 현재는 임시(서울시청) 마커만 존재. DB에 저장된 매장 좌표 기반으로 변경 필요
5. **환경변수 분리**: `application.properties`와 `db_insert.py`의 DB 비밀번호(`1234`)가 평문 하드코딩 → `.env` 또는 secret manager 사용 권장
6. **Kakao Maps API 키**: `.env` 파일에 평문 노출 → git-secret 또는 환경변수 주입 필요
