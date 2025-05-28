from sklearn.base import BaseEstimator, TransformerMixin

class RareCategoryGrouper(BaseEstimator, TransformerMixin):
    def __init__(self, column, min_count, label='Inne'):
        self.column = column
        self.min_count = min_count
        self.label = label
        self.rare_values_ = None
    def fit(self, X, y=None):
        counts = X[self.column].value_counts()
        self.rare_values_ = counts[counts < self.min_count].index
        return self
    def transform(self, X):
        X = X.copy()
        X[self.column] = X[self.column].apply(lambda x: self.label if x in self.rare_values_ else x)
        return X

class ColumnDropper(BaseEstimator, TransformerMixin):
    def __init__(self, columns):
        self.columns = columns
    def fit(self, X, y=None):
        return self
    def transform(self, X):
        return X.drop(columns=self.columns)