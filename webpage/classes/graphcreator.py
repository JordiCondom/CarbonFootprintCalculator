import base64
import io
from matplotlib.figure import Figure
import numpy as np


class graphCreator:
    def __init__(self, dataframe,dates, date_data):
        self.df = dataframe
        self.dates = dates
        self.date_data = date_data
    
    def create_tracking_graphs(self):

        # Extract the data for each date
        for _, row in self.df.iterrows():
            date = row['datetime']
            self.date_data[date]['food'].append(row['food'])
            self.date_data[date]['transportation'].append(row['transportation'])
            self.date_data[date]['household'].append(row['household'])
            self.date_data[date]['expenses'].append(row['expenses'])
            self.date_data[date]['total'].append(row['total'])

        # Generate the figure **without using pyplot**.
        fig = Figure(figsize=(10, 10))
        gs = fig.add_gridspec(2, 2)
        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, 0])
        ax3 = fig.add_subplot(gs[1, 1])

        # Plot the data for each date and connect the points
        for date in self.dates:
            x = ['food', 'transportation', 'household', 'expenses']
            y = [np.mean(self.date_data[date]['food']),
                np.mean(self.date_data[date]['transportation']),
                np.mean(self.date_data[date]['household']),
                np.mean(self.date_data[date]['expenses'])]
            ax1.plot(x, y, label=date, marker='o')
            ax1.plot(x, y, 'k--', alpha=0.5)

        ax1.set_xlabel('Question')
        ax1.set_ylabel('Answer')
        ax1.legend()

        # Create a pie chart for the expense categories
        expense_labels = ['Food', 'Transportation', 'Household', 'Expenses']
        expense_values = [
            np.sum(self.df['food']),
            np.sum(self.df['transportation']),
            np.sum(self.df['household']),
            np.sum(self.df['expenses'])
        ]
        ax2.pie(expense_values, labels=expense_labels, autopct='%1.1f%%')
        ax2.set_aspect('equal')  # Equal aspect ratio ensures the pie is circular

        ax3.plot(self.df['datetime'], self.df['total'])
        ax3.set_xlabel('Datetime')
        ax3.set_ylabel('Total')

        # Save the figures to a temporary buffer.
        buf1 = io.BytesIO()
        fig.savefig(buf1, format='png')
        buf1.seek(0)

        # Embed the results in the HTML output.
        data1 = base64.b64encode(buf1.getvalue()).decode()
        return data1
