if(!require(ggplot2)){
  install.packages("ggplot2")
}
if(!require(zoo)){
  install.packages("zoo")
}
library(ggplot2)
library(zoo)
weeks = read.csv("org_weekly_data.csv")
weeks = weeks[c("week_start", "issues_opened", "issue_comments", "issues_closed", "commits", "contributor_count")]
z = read.zoo(weeks)
colnames(z) = c("Issues Opened", "Issue Comments", "Issues Closed", "Commits", "Contributors")
p = autoplot(z, facet = NULL) + labs(title="PEDSNet GitHub Activity") + xlab("") + theme_bw() + theme(legend.title=element_blank(), axis.text=element_text(size=14), axis.title=element_text(size=14), legend.text=element_text(size=14), plot.title=element_text(size=16, face="bold"), legend.justification=c(0,1), legend.position=c(0,1))
ggsave(file="activity_fig.png", plot=p, width=7.9, height=5.24)
corr_mat = cor(z, method="pearson")
write.csv(corr_mat, file="corr_matrix.csv")
