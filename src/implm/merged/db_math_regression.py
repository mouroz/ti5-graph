import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from typing import Tuple, List, Dict

# Global variables to store the trained model and transformer
modelo_poly: LinearRegression | None = None
transformador_poly: PolynomialFeatures | None = None

def load_and_clean_csv(csv_path: str, is_train_csv: bool = False) -> pd.DataFrame:
    """Load and clean CSV data."""
    df = pd.read_csv(csv_path, encoding='ISO-8859-1', sep=',')
    
    # Convert 'Nivel de Ruido' to string first, then replace comma with dot, then convert to float
    if 'Nivel de Ruido' in df.columns:
        df['Nivel de Ruido'] = df['Nivel de Ruido'].astype(str).str.replace(',', '.').astype(float)
    elif(is_train_csv):
            raise ValueError("Coluna 'Nivel de Ruido' não encontrada no CSV de treino.")

    if 'Velocidade Fan Base' in df.columns:
        df['Velocidade Fan Base'] = pd.to_numeric(df['Velocidade Fan Base'], errors='coerce')
    elif 'RPM' in df.columns:
        df['Velocidade Fan Base'] = pd.to_numeric(df['RPM'], errors='coerce')
    else:
        raise ValueError("Coluna 'Velocidade Fan Base' ou 'RPM' não encontrada no CSV.")

    if 'Velocidade Fan PC' in df.columns:
        df['Velocidade Fan PC'] = pd.to_numeric(df['Velocidade Fan PC'], errors='coerce')
    else:
        raise ValueError("Coluna 'Velocidade Fan PC' não encontrada no CSV.")
    
    return df

def split_train_test(df: pd.DataFrame, 
                    train_values: List[int] = [0, 960, 1530, 1980, 2340],
                    test_values: List[int] = [600, 1290, 1770, 2190]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data into training and test sets based on Velocidade Fan Base values."""
    df_treino = df[df['Velocidade Fan Base'].isin(train_values)].copy()
    df_teste = df[df['Velocidade Fan Base'].isin(test_values)].copy()
    
    print(f"Dataset de treino: {len(df_treino)} amostras")
    print(f"Dataset de teste: {len(df_teste)} amostras")
    
    return df_treino, df_teste

def train_polynomial_regression(df: pd.DataFrame, grau: int = 2) -> Tuple[LinearRegression, PolynomialFeatures, pd.DataFrame]:
    """Train polynomial regression model."""
    # Preparar os dados
    X = df[['Velocidade Fan Base', 'Velocidade Fan PC']].copy()
    y = df['Nivel de Ruido'].copy()

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

    # Aplicar ao DataFrame original (onde possível)
    df['RuidoEstimadoPoly'] = np.nan
    df.loc[mask, 'RuidoEstimadoPoly'] = y_pred

    return model, poly, df

def predict_with_model(df: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
    """Predict noise levels using the trained model."""
    global modelo_poly, transformador_poly
    
    if modelo_poly is None or transformador_poly is None:
        raise ValueError("Modelo polinomial ou transformador não foram definidos.")
    
    # Preparar os dados
    mask = df[['Velocidade Fan Base', 'Velocidade Fan PC']].notnull().all(axis=1)
    X = df.loc[mask, ['Velocidade Fan Base', 'Velocidade Fan PC']]
    X_poly = transformador_poly.transform(X)
    
    # Prever ruido
    df['RuidoEstimadoPoly'] = np.nan
    df.loc[mask, 'RuidoEstimadoPoly'] = np.round(modelo_poly.predict(X_poly), 2)

    # Save predictions to CSV if output path is provided
    if output_path:
        df.to_csv(output_path, index=False)

    return df

def predict_with_csv(csv_path: str, output_path: str = None) -> pd.DataFrame:
    df = load_and_clean_csv(csv_path)
    df = predict_with_model(df)
    if output_path:
        df.to_csv(output_path, index=False)
    return df

def calculate_metrics(df: pd.DataFrame, real_col: str = 'Nivel de Ruido', 
                     pred_col: str = 'RuidoEstimadoPoly') -> Dict[str, float]:
    """Calculate RMSE, MAE, mean difference, and max difference."""
    mask = df[[real_col, pred_col]].notnull().all(axis=1)
    
    if not mask.any():
        return {'rmse': np.nan, 'mae': np.nan, 'mean_diff': np.nan, 'max_diff': np.nan}
    
    y_true = df.loc[mask, real_col]
    y_pred = df.loc[mask, pred_col]
    
    # Calculate difference
    diff = y_true - y_pred
    
    return {
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'mae': mean_absolute_error(y_true, y_pred),
        'mean_diff': diff.mean(),
        'max_diff': diff.abs().max()
    }

def print_polynomial_equation(model: LinearRegression, poly_features: PolynomialFeatures, 
                             feature_names: List[str] = ['Velocidade Fan Base', 'Velocidade Fan PC']):
    """Print the polynomial equation generated by the model."""
    feature_names_poly = poly_features.get_feature_names_out(feature_names)
    coefficients = model.coef_
    intercept = model.intercept_
    
    print("\n=== FUNÇÃO POLINOMIAL GERADA ===")
    print(f"Intercepto: {intercept:.10f}")
    print("\nCoeficientes:")
    
    equation = f"Ruído = {intercept:.10f}"
    
    for coef, feature in zip(coefficients, feature_names_poly):
        print(f"{feature}: {coef:.10f}")
        
        if coef >= 0:
            equation += f" + {coef:.10f} * {feature}"
        else:
            equation += f" - {abs(coef):.10f} * {feature}"
    
    print(f"\nEquação completa:")
    print(equation)
    
    readable_equation = equation.replace('Velocidade Fan Base', 'VB').replace('Velocidade Fan PC', 'VPC')
    print(f"\nVersão simplificada:")
    print(readable_equation)

def print_comparison_table(df: pd.DataFrame, title: str, metrics: Dict[str, float]):
    """Print comparison table with predictions vs real values."""
    df['Diferença Ruido'] = df['Nivel de Ruido'] - df['RuidoEstimadoPoly']
    
    print(f"\n=== {title} ===")
    print("Comparação Nível de Ruído vs RuidoEstimadoPoly:")
    print("------------------------------------------------------------------------------")
    print("Base RPM\tPC RPM\t\tRuído Real\tRuído Estimado (Poly)\tDiferença")
    print("------------------------------------------------------------------------------")

    for _, row in df[['Velocidade Fan Base', 'Velocidade Fan PC', 'Nivel de Ruido', 'RuidoEstimadoPoly', 'Diferença Ruido']].iterrows():
        print(f"{row['Velocidade Fan Base']:.0f}\t\t{row['Velocidade Fan PC']:.0f}\t\t{row['Nivel de Ruido']:.3f}\t\t{row['RuidoEstimadoPoly']:.3f}\t\t\t{row['Diferença Ruido']:.3f}")

    print(f"\nMétricas do conjunto de {title}:")
    print(f"RMSE: {metrics['rmse']:.3f}")
    print(f"MAE: {metrics['mae']:.3f}")
    print(f"Diferença média: {metrics['mean_diff']:.3f}")
    print(f"Diferença máxima: {metrics['max_diff']:.3f}")

def create_polinomial_regression_from_csv(grau: int = 3, csv_path: str = "data/fans_db_tests.csv", log_in_terminal: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function to create polynomial regression model from CSV data.
    
    Parameters:
    - grau: Degree of polynomial (default is 3)
    - csv_path: Path to CSV file
    
    Returns:
    - Tuple of (training_df, test_df)
    """
    global modelo_poly, transformador_poly
    
    # Load and clean data
    df = load_and_clean_csv(csv_path, is_train_csv=True)
    
    # Split into train/test sets
    df_treino, df_teste = split_train_test(df)
    
    # Train model on training set
    modelo_poly, transformador_poly, df_treino = train_polynomial_regression(df_treino, grau=grau)
    
    # Print polynomial equation
    if log_in_terminal:
        print_polynomial_equation(modelo_poly, transformador_poly)
    
    # Predict on test set
    df_teste = predict_with_model(df_teste)
    
    # Calculate metrics for both sets
    metrics_treino = calculate_metrics(df_treino)
    metrics_teste = calculate_metrics(df_teste)
    
    # Generate reports
    if log_in_terminal:
        print_comparison_table(df_treino, "CONJUNTO DE TREINO", metrics_treino)
        print_comparison_table(df_teste, "CONJUNTO DE TESTE", metrics_teste)
    
    return df_treino, df_teste