
library(ggplot2)
library(asbio) # Teste Tukey de Aditividade
library(doBy)
library(car) # Teste de Fligner Killeen
library(effects)
library(pwr)
library(PMCMR)
library(corrplot)
install.packages("Hmisc")
library(Hmisc)
install.packages(("PerformanceAnalytics"))
library(PerformanceAnalytics)



options(scipen=10)

tecnicas=(DADOS_TABELADOS)

shapiro.test(tecnicas$TENSÃO)


posthoc.kruskal.nemenyi.test(tecnicas$DEFORMAÇÃO ~ factor(tecnicas$TRATAMENTO))

mod1<-kruskal.test(tecnicas$DEFORMAÇÃO~tecnicas$TRATAMENTO,data=tecnicas)
mod1
modKruskal=kruskal(tecnicas$DEFORMAÇÃO, tecnicas$TRATAMENTO, alpha = 0.05, p.adj=c("none","holm","hommel","hochberg", "bonferroni", "BH", "BY", "fdr"), group=TRUE, main = "Tensão",console=FALSE)
modKruskal

#GRÁFICO
bar.group(modKruskal$groups,ylim=c(0,26),main="Deformação (%) X Tempo de exposição (Dias)",ylab="Deformação (%)",xlab="Tempo de exposição (Dias)")
legend("toprig", legend=c("Deformação (%)"),
       fill=c("grey"), bty="n")


plot(tecnicas$`TENSÃO TABOA`~tecnicas$`TENSÃO JUNCO`)
 m<-cor.test(tecnicas$`TENSÃO TABOA`,tecnicas$`TENSÃO JUNCO`)





m<-cor(tecnicas)

m 




corrplot(m) # padrão com círculos
corrplot(m, method="color") #cores
corrplot(m, method="ellipse") #elípses
corrplot(m, method="shade") # tons
corrplot(m, method="number",main="Deformação (%) X Tempo de exposição (Dias)") #números
corrplot(m,method="number",type="upper")
corrplot(m,type="lower",method = "number")

m<- rcorr(as.matrix(tecnicas)) #coeficiente de correlação, n e valor p
m$r # matriz de coeficiente de correlação
m$P # matriz de valor p
m$n
corrplot(m$r,p.mat=m$P,sig.level= 0.005)
corrplot(m$r,p.mat=m$P,sig.level=0.005,method="number",type="upper")

chart.Correlation(tecnicas, histogram = TRUE)


