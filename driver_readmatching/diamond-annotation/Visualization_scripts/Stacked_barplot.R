library(dplyr)
library(ggplot2)
library(reshape2)


setwd("~/Desktop/Problem_Solving/Data_analysis/Analysis/boxplot/")
file<- read.csv("~/Desktop/Problem_Solving/Data_analysis/Analysis/boxplot/16S_full_type_trans.csv", header = TRUE, sep = ',') %>% tbl_df()
groups <- read.csv("~/Desktop/Problem_Solving/Data_analysis/Analysis/boxplot/group_data.csv", header = TRUE, sep = ',') %>% tbl_df()


#boxplot_file <- full_join(file, groups, by = "Sample")
#write.csv(boxplot_file, "boxplot_file.csv")

boxplot_file <- read.csv("boxplot_file.csv", header = TRUE, sep = ',') %>% tbl_df()

box.m <-melt(boxplot_file, id.vars='Years', measure.vars = c('MLS','aminoglycoside','antibacterial_free_fatty_acids',
                                                            'bacitracin','beta.lactam','diaminopyrimidine',
                                                            'fluoroquinolone','fosmidomycin','glycopeptide',
                                                            'multidrug','mupirocin','nitroimidazole','peptide',
                                                            'phenicol','pleuromutilin','polymyxin','rifamycin',
                                                            'sulfonamide','tetracycline','triclosan','unclassified',
                                                            'aminoglycoside.aminocoumarin','fosfomycin','nucleoside',
                                                            'oxazolidinone'))

ggplot(box.m, aes(fill= variable, y=value, x=Years), theme(legend.title = element_blank())) + 
  geom_bar(position="stack", stat="identity") +
  xlab('Year') +
  ylab(" Relative Abundance (ARGs/16S rRNA gene)") +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        panel.background = element_blank(), axis.line = element_line(colour = "black"))+
  labs(fill = "ARG drug classes") +
  theme(legend.position="top") 
  xlab()

  
