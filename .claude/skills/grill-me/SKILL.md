---
name: grill-me
description: Entrevista implacável sobre um plano, projeto ou decisão até chegar a um entendimento compartilhado. Use quando o usuário disser "grill me", "me sabatina", "me questiona", "me entrevista sobre esse plano", "testa esse plano", "pressiona esse plano", ou pedir para ser questionado antes de executar algo.
---

# Grill me

Entreviste o usuário de forma implacável sobre cada aspecto do plano até chegarem a um entendimento compartilhado.

## Como conduzir

- Percorra cada galho da árvore de decisões, resolvendo as dependências entre decisões uma a uma (primeiro o que destrava as outras).
- Faça **uma pergunta por vez**. Espere a resposta antes da próxima.
- Para cada pergunta, dê **a sua resposta recomendada** e o porquê em uma linha — o usuário só confirma ou corrige.
- Se uma pergunta pode ser respondida explorando o código, os arquivos, o Supabase (`products_data` é a fonte de verdade de produto) ou outra ferramenta disponível, **vá buscar em vez de perguntar**.
- Foco em **execução**: como, quando, com quais recursos, o que pode quebrar. Não questione se a ideia vale a pena ou se é prioridade — isso é decisão do usuário.
- Quando algo for hipótese (não verificável com as ferramentas), diga que é hipótese.

## Encerramento

Quando todos os galhos estiverem resolvidos, entregue um resumo curto:
1. Decisões tomadas
2. Pontos em aberto (se houver)
3. Próximos passos concretos
