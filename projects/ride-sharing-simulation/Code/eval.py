import seaborn as sns
import matplotlib.pyplot as plt



def hist_plot(values, label, means=None, CIs=None, PIs=None, COMP=None):
    '''
    Generate histogram plots for multiple metrics 
    
    :param values: list of lists, containing values reported for each metric
    :param label: corresponding names of the metrics in the list
    :param means: means of each metric
    :param CIs: 95% confidence interval of the mean estimate 
    :param PIs: 95% prediction interval, used to evaluate new values
    :param COMP: Comparative value, plotted as a vertical line
    '''
    fig, axes = plt.subplots(1, len(label), figsize=(20, 5))
    axes = axes.flatten()

    for i in range(len(axes)):

        sns.histplot(values[i], ax=axes[i], bins=16)

        # titles and labels
        axes[i].set_title(f"Density of {label[i]}", fontsize=20)
        axes[i].set_xlabel(label[i], fontsize=20)
        if i==0:
            axes[i].set_ylabel("Frequency", fontsize=20)
        else:
            axes[i].set_ylabel("")

        # increase tick size
        axes[i].tick_params(axis='both', labelsize=14)

        if means is not None:
            axes[i].axvline(means[i], linestyle="solid", color="orange", label="Mean")

        if CIs is not None:
            axes[i].axvline(CIs[i][0], linestyle="dashed", color="red", label="95% CI")
            axes[i].axvline(CIs[i][1], linestyle="dashed", color="red")

        if PIs is not None:
            axes[i].axvline(PIs[i][0], linestyle="dashed", color="purple", label="95% PI")
            axes[i].axvline(PIs[i][1], linestyle="dashed", color="purple")

        if COMP is not None:
            axes[i].axvline(COMP[i], linestyle="solid", color="green", label="Observed")

        # legend
    plt.legend(fontsize=18)

    plt.tight_layout()
    plt.show()