import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error

modelo_poly:LinearRegression = any
transformador_poly:PolynomialFeatures = any

def prever_ruido_em_csv(modelo, transformador, caminho_csv):

    # Ler novo CSV
    novo_df = pd.read_csv(caminho_csv, encoding='ISO-8859-1', sep=',')
    print(novo_df.columns)
    print(novo_df)
    novo_df['RPM'] = pd.to_numeric(novo_df['RPM'], errors='coerce')
    novo_df['CPU [RPM]'] = pd.to_numeric(novo_df['CPU [RPM]'], errors='coerce')

    novo_df = novo_df.rename(columns={'RPM': 'Velocidade Fan Base', 'CPU [RPM]': 'Velocidade Fan PC'})


    # Filtrar apenas valores válidos
    mask = novo_df[['Velocidade Fan Base', 'Velocidade Fan PC']].notnull().all(axis=1)



    # Transformar os dados para o modelo
    X_novo = novo_df.loc[mask, ['Velocidade Fan Base', 'Velocidade Fan PC']]
    X_novo_poly = transformador.transform(X_novo)

    # Prever ruído
    novo_df['RuidoEstimadoPoly'] = np.nan
    novo_df.loc[mask, 'RuidoEstimadoPoly'] = modelo.predict(X_novo_poly)

    return novo_df

def regressao_polinomial_ruido(df, grau=2):
    # Preparar os dados
    X = df[['Velocidade Fan Base', 'Velocidade Fan PC']].copy()
    y = df['Nível de Ruído'].copy()

    # Remover entradas nulas
    mask = X.notnull().all(axis=1) & y.notnull()
    X = X[mask]
    y = y[mask]

    # Criar características polinomiais
    poly = PolynomialFeatures(degree=grau, include_bias=False)
    X_poly = poly.fit_transform(X)

    # Regressão
    model = LinearRegression()
    model.fit(X_poly, y)

    # Previsões
    y_pred = model.predict(X_poly)

    # Métricas
    rmse = np.sqrt(mean_squared_error(y, y_pred))
    mae = mean_absolute_error(y, y_pred)

    # Aplicar ao DataFrame original (onde possível)
    df['RuidoEstimadoPoly'] = np.nan
    df.loc[mask, 'RuidoEstimadoPoly'] = y_pred

    print(f"Regressão Polinomial grau {grau}: RMSE = {rmse:.3f} | MAE = {mae:.3f}")
    return model, poly, df

def create_polinomial_regression(grau=2):
    """
    Cria um modelo de regressão polinomial para prever o nível de ruído com base na velocidade do fan.
    
    Parâmetros:
    - grau: Grau do polinômio a ser usado na regressão (default é 2).
    """
    df = pd.read_csv("data/fan_db_tests.csv", encoding='ISO-8859-1', sep=',')
    
    # Exemplo de uso:

    df['Nivel de Ruido'] = df['Nivel de Ruido'].str.replace(',', '.').astype(float)
    df['Velocidade Fan Base'] = pd.to_numeric(df['Velocidade Fan Base'], errors='coerce')
    df['Velocidade Fan PC'] = pd.to_numeric(df['Velocidade Fan PC'], errors='coerce')

    # Rodar regressão polinomial de grau 3
    modelo_poly, transformador_poly, df = regressao_polinomial_ruido(df, grau=3)

    df_result = prever_ruido_em_csv(modelo_poly, transformador_poly, "merged_data.csv")

    # Visualizar comparação e calcular a diferença média
    print("\nComparação Nível de Ruído vs RuidoEstimadoPoly:")

    # Visualizar comparação e calcular a diferença média (Visualização Tabular)
    print("\nComparação Nível de Ruído vs RuidoEstimadoPoly:")

    # Calcular a diferença
    df['Diferença Ruido'] = df['Nível de Ruído'] - df['RuidoEstimadoPoly']

    # Imprimir cabeçalho da tabela
    print("------------------------------------------------------------------------------")
    print("Base RPM\tPC RPM\t\tRuído Real\tRuído Estimado (Poly)\tDiferença")
    print("------------------------------------------------------------------------------")

    # Imprimir linha a linha com tabs
    for index, row in df[['Velocidade Fan Base', 'Velocidade Fan PC', 'Nível de Ruído', 'RuidoEstimadoPoly', 'Diferença Ruido']].iterrows():
        print(f"{row['Velocidade Fan Base']}\t\t{row['Velocidade Fan PC']}\t\t{row['Nível de Ruído']:.3f}\t\t{row['RuidoEstimadoPoly']:.3f}\t\t\t{row['Diferença Ruido']:.3f}")

    # Imprimir separador final da tabela
    print("------------------------------------------------------------------------------")

    # Calcular a diferença média
    diferenca_media = df['Diferença Ruido'].mean()
    print(f"\nDiferença média entre Ruído Real e Ruído Estimado (Poly): {diferenca_media:.3f}")

    print(df_result)