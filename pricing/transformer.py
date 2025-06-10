from sklearn.base import BaseEstimator, TransformerMixin

class RareCategoryGrouper(BaseEstimator, TransformerMixin):
    def __init__(self, column, min_count):
        self.column = column
        self.min_count = min_count
        self.rare_values_ = None
    def fit(self, X, y=None):
        counts = X[self.column].value_counts()
        self.rare_values_ = counts[counts < self.min_count].index
        return self
    def transform(self, X):
        X = X.copy()
        X[self.column] = X[self.column].apply(lambda x: 'Inne' if x in self.rare_values_ else x)
        return X
