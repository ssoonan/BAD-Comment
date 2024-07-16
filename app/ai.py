from openai import OpenAI
import os

openai_client = OpenAI(api_key=os.environ['OPENAI_KEY'])


def request_to_openai(user_prompt, system_prompt):
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content


def _parse_yes_no_to_bool(response):
    if response.lower() == "yes":
        return True
    elif response.lower() == "no":
        return False
    else:
        return False


def evaluate_comment(comment) -> bool:
    if len(comment) > 100:
        return False
    user_prompt = f"다음 한국어 댓글을 평가하고 제공된 기준에 따라 차단해야 하는지 결정하세요. 차단해야 한다면 'yes'로만, 허용 가능하다면 'no'로만 응답하세요. 차단 확률이 55% 이렇게 애매하다면 그냥 'no'로만 응답하세요.\n\nComment: {comment}"
    system_prompt = "댓글 차단 기준은 다음과 같습니다: 저에게 직접적으로 공격적인 댓글 (예: 모욕적인 언어 사용, 개인적인 공격). 외모에 대한 댓글 (예: 신체적 외모에 대한 비하 발언). 콘텐츠가 아닌 메신저에 대한 과도한 비판 (예: 대뜸 경력을 묻는 경우) 차단해야 할 댓글의 예:\n클래스101을 IT회사라고 올려놓은 꼬라지라니.... 이 유튜버의 영상은 가치가 1도 없습니다.\n- 제목 어그로 엄마없음 개추\n- 제목만 보면 니가 구글 메타 출신인줄 알겠다 ㅋ 개발은 못해도 입은 잘터네 SI/SM가면 잘 살아남을듯\n- 진짜 궁금해서 그런데. 그렇게 별로면 본인이나 일 관두시던가요. 이제 배우는 애들한테 이런 좆같은소리하는 이유가 뭐에요?\n- 뭐지 해당기업에서 정리해고 잘 당하게 생긴 얼굴로 하는 말은...\n조회수 빨아먹어야 하니까 이딴 소리 하는거지.\n자기 기준의 역한 리뷰 감사합니다. 아 저는 웹쪽은 아니지만 게임 개발자 현직에서 3년차 넘어간 시니어 개발자 입니다. 왜 역하냐구요? 일단은 당신이 말 안하셔도 요즘 개발자들은 일반적으로 다들 AI가 뭘 대체하고 있고, 심지어 조수의 역할로써 '정말 좋은 역할을 하는 나의 개발의 조수가 되겠구나' 생각은 하면서 잘 사용하고 있는 추세입니다. 그리고 '기본과 원리에 출중 하면서 AI를 어떻게 다루는가'를 보는거지 코딩을 반대하는게 아닙니다.\n차단하지 않을 댓글의 예시 :\n- 책팔이네요\n- 크몽 광고나 하지 마세요\n-님이 만들면 고민하고 만든 것이고 남이 만들면 고민하지 않고 만든 것인가요? 나르시즘 쩌네요 ㅋㅋㅋㅋ\n- 흠... 무슨말을 하고싶은지는 알겠는데 본인 논리를 돋보이기 위해 가장 보편적인 상황을 극단적으로 묘사하는 경향이 있으신거같에요..ㅎ 전에 어떤회사에 계셨는지는 모르겠지만 주변 개발자분들을 정말 별로라고 생각하셨던거 같습니다. 모든 직업군에는 능력별 스펙트럼이 존재하죠. 회사다니는 개발자들을 너무 메트릭스속 npc처럼 보시는거같에요ㅎ 그리고 대부분 개발자들이 알고 있지만 현실에 치여 실행 못하는걸 장황하게 풀어서 개발자가 되려는 비전공자들에게 알려주시는 느낌입니다.\n- 개발쪽이 레드오션이라는 뜻\n요즘 개나소나 개발자 준비하긴함ㅋㅋㅋㅋㅋ\n"
    return _parse_yes_no_to_bool(request_to_openai(user_prompt=user_prompt, system_prompt=system_prompt))
