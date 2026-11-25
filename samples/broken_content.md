# 인스타그램(@your_instagram_id) 원고 & 이미지 프롬프트 (QC 테스트용 오답 샘플)

- 프로젝트: broken-sample
- 포맷: cardnews
- 브랜드 톤: A

## 1. 인스타그램 게시 캡션
```text
이거 무조건 공짜로 10배 빨라집니다!! #AI뉴스
```

## 2. Gemini 이미지 프롬프트

### [컷 1] `images/card_01.png`
- 한글 제목: 이 제목은 열두 글자를 훨씬 넘어서 제미나이에서 깨집니다
- 한글 부제: 말풍선과 본문 텍스트도 스무 글자를 넘기면 자모가 뭉개져서 읽기 어렵습니다
- 추가 텍스트: 세 번째 텍스트 블록 초과
- Gemini 입력 프롬프트:
```text
Create a square 1:1 image with lots of text and no borders.
```

### [컷 2] `images/card_02.png`
- 한글 제목: TODO
- 한글 부제: 아직 작성 전

## 3. 팩트 근거 매핑
| 원고/슬라이드 핵심 주장 | `01_news_brief.md` 근거 ID |
|---|---|
| 확인 필요 | F1 |
