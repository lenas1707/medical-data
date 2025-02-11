import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração inicial
plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (12, 8)

# Carregar os dados
df = pd.read_csv('casos-estudo.csv', encoding='utf-8', delimiter=',')
df.columns = df.columns.str.strip()  # Padronizar nomes das colunas

# Função para converter idade
def convert_age(age):
    try:
        if isinstance(age, str) and '/' in age:
            parts = age.split('/')
            return float(parts[0]) / float(parts[1])
        else:
            return float(age)
    except:
        return None

df['Idade'] = df['Idade'].apply(convert_age)

# ====================== GRÁFICO DE EXAMES (IGNORANDO DIAGNÓSTICOS CLÍNICOS) ======================
# Pré-processamento dos exames
df_exames = df.copy()
df_exames['Exames'] = df_exames['Exames'].str.lower()

# Filtro inicial para remover linhas com termos indesejados
df_exames = df_exames[~df_exames['Exames'].str.contains(
    'exames prévios|diagnóstico clínico', 
    case=False, 
    na=False
)]

# Dividir e balancear colunas
def balance_exames_status(row):
    exames = row['Exames_split'] if isinstance(row['Exames_split'], list) else []
    status = row['Status_split'] if isinstance(row['Status_split'], list) else []

    # Ajustar tamanho das listas
    max_len = max(len(exames), len(status))
    exames = exames + [None]*(max_len - len(exames))
    status = status + [None]*(max_len - len(status))
    
    return pd.Series([exames, status])

df_exames['Exames_split'] = df_exames['Exames'].str.split(',')
df_exames['Status_split'] = df_exames['Status'].str.split(',')
df_exames[['Exames_split', 'Status_split']] = df_exames.apply(balance_exames_status, axis=1)

# Explodir colunas
df_exploded = df_exames.explode(['Exames_split', 'Status_split'])

# Limpeza final e filtro pós-explosão
df_exploded['Exames_split'] = df_exploded['Exames_split'].str.strip()
df_exploded['Status_split'] = df_exploded['Status_split'].str.strip()

# Filtro adicional para garantir remoção de diagnósticos clínicos mesmo após split
df_exploded = df_exploded[
    df_exploded['Exames_split'].notna() & 
    (df_exploded['Exames_split'] != '') &
    (~df_exploded['Exames_split'].str.contains('diagnóstico clínico', case=False, na=False))
]

# Renomear coluna
df_exploded.rename(columns={'Status_split': 'Subtitle'}, inplace=True)

# Criar e plotar pivot
exam_status_pivot = pd.pivot_table(
    df_exploded,
    index='Exames_split',
    columns='Subtitle',
    aggfunc='size',
    fill_value=0
)

exam_status_pivot.plot(kind='bar', figsize=(14,7), color=['skyblue', 'salmon'])
plt.title('Status dos Exames')
plt.xlabel('Exames')
plt.ylabel('Contagem')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('exam_status.png')
plt.close()

# ====================== DEMAIS GRÁFICOS (CÓDIGO ORIGINAL) ======================
# 1. Gráfico de Naturalidade
plt.figure(figsize=(10,5))
df['Natularidade'].value_counts().plot(kind='bar', color='skyblue')
plt.title('Distribuição por Naturalidade')
plt.xlabel('Cidade')
plt.ylabel('Casos')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('naturalidade.png')
plt.close()

# 2. Gráfico de Especialidades
plt.figure(figsize=(10,5))
df['Especialidade que encaminhou'].value_counts().plot(kind='bar', color='salmon')
plt.title('Encaminhamentos por Especialidade')
plt.xlabel('Especialidade')
plt.ylabel('Encaminhamentos')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('especialidade.png')
plt.close()

# 3. Top 3 Diagnósticos nas Top 3 Cidades
top_cidades = df['Natularidade'].value_counts().head(3).index
plt.figure(figsize=(15,5))
for i, cidade in enumerate(top_cidades, 1):
    plt.subplot(1,3,i)
    df[df['Natularidade'] == cidade]['Diagnostico'].value_counts().head(3).plot(
        kind='bar', color='lightgreen'
    )
    plt.title(f'Top 3 Diagnósticos - {cidade}')
    plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('top3_diagnosticos.png')
plt.close()

# 4. Boxplot Idade vs TEA
df['TEA'] = df['Diagnostico'].str.contains('tea', case=False).fillna(False)
sns.boxplot(x='TEA', y='Idade', data=df, palette='Set2')
plt.title('Distribuição de Idade por Diagnóstico de TEA')
plt.xlabel('Diagnóstico de TEA')
plt.ylabel('Idade (Anos)')
plt.xticks([0,1], ['Outros', 'TEA'])
plt.tight_layout()
plt.savefig('idade_tea.png')
plt.close()
