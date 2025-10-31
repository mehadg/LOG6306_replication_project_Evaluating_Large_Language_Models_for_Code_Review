import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# --- Data setup ---
data = {
    'Model': ['LLaMA', 'LLaMA', 'Mistral', 'Mistral',
               'LLaMA', 'LLaMA', 'Mistral', 'Mistral'],
    'Dataset': ['GT', 'GT', 'GT', 'GT',
                'Mixed', 'Mixed', 'Mixed', 'Mixed'],
    'Description': ['With Desc', 'Without Desc', 'With Desc', 'Without Desc',
                    'With Desc', 'Without Desc', 'With Desc', 'Without Desc'],
    'Accuracy_%': [32.7, 33.1, 33.1, 32.7, 98.8, 99.2, 99.0, 98.6],
    'Correction_%': [0, 0, 0, 0, 51.6, 52.2, 52.2, 51.8],
    'Regression_%': [67.3, 66.9, 66.9, 67.3, 0.4, 0.6, 0.8, 0.8],
}

df = pd.DataFrame(data)

colors = {'LLaMA': '#1f77b4', 'Mistral': '#ff7f0e'}
metrics = ['Accuracy_%', 'Correction_%', 'Regression_%']

# --- Fixed plotting section ---
for metric in metrics:
    plt.figure(figsize=(8,5))
    labels = ['GT - With Desc', 'GT - Without Desc', 'Mixed - With Desc', 'Mixed - Without Desc']
    x = np.arange(len(labels))
    width = 0.35

    llama_vals = []
    mistral_vals = []
    for dataset, desc in [('GT', 'With Desc'), ('GT', 'Without Desc'),
                          ('Mixed', 'With Desc'), ('Mixed', 'Without Desc')]:
        llama_vals.append(df[(df['Model']=='LLaMA') & (df['Dataset']==dataset) & (df['Description']==desc)][metric].values[0])
        mistral_vals.append(df[(df['Model']=='Mistral') & (df['Dataset']==dataset) & (df['Description']==desc)][metric].values[0])

    plt.bar(x - width/2, llama_vals, width, label='LLaMA', color=colors['LLaMA'])
    plt.bar(x + width/2, mistral_vals, width, label='Mistral', color=colors['Mistral'])

    plt.xticks(x, labels, rotation=25, ha='right')
    plt.ylabel(metric.replace('_',' '))
    plt.title(f"{metric.replace('_',' ')} by Model, Dataset, and Description")
    plt.legend()
    plt.tight_layout()
    plt.show()
