import pytest
from src.tools.task_creator import TaskCreator


@pytest.fixture
def creator():
    return TaskCreator()


def test_creator(creator):
    example = {
        "jira_title": 'Проверить тестпак для "PD_POS_01 KI MOVISTAR"',
        "jira_description": "[https://dif-tech.slack.com/archives/C04UBAW812S/p1729864911371049|https://dif-tech.slack.com/archives/C04UBAW812S/p1729864911371049|smart-link] ",
        "slack_thread_messages": ":review: *[DEV]* <https://platacard.atlassian.net/browse/RISKDEV-2726>\n\n<!subteam^S075H546DFA>\nВ *pd_pos_01_ki_movistar_logit* используется *has_cc_opened*\n```has_cc_opened_term = -0.51294 * (has_cc_opened - 0.65217) / 0.47715```\nЗдесь не учтено, что has_cc_opened может быть None. Могу в таком случае считать, что has_cc_opened_term = 0?\nЛучше прописать, если none, то терм равен 0\n<@U06K9H09UBY> <@U048UNLBJNL>\nЕще мы здесь начинаем смотреть на point_id, который раньше не приходил в pyscoring\n\nЕсть 3 варианта:\n• катим гошную часть первой и собираем данные\n• катим го и pyscoring одновременно, что сломает прогоны батча на какое-то время\n• делаем point_id опциональным и добавляем логику при которой не будем считать pd_pos_01_movistar_logit если point_id is None\nесли дедлайн всей стори не горит, гошку удобней раньше\n<@U05CFFUE30F> <@U067WAFE3FB> какой здесь due date?\nМожем подождать несколько дней пока у нас логи накопятся?\nУ нас общий дедлайн для этой задачи, внедрения модели и блокировки - 15.11\nПоэтому если мы пока будем заниматься другими - не вопрос, можем подождать\n<@U06K9H09UBY> посмотри плиз гошку в пн, чтоб ее раскатить до всей стори\nА я в понедельник дей офф, <@U05HX4NKU58> подхвати плиз\nмб гошку есть варик сегодня катануть? чтобы выходные данные копились?",
    }
    text = "\n".join([f"{key} {value}" for key, value in example.items()])
    creator_result = creator.create_task(text)
    print(creator_result)

    assert creator_result.quality_check
