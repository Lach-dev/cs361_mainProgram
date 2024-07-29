##### Data Analysis #8 
##### Upload the ST314ExamData_DA8 data set. 
##### Review MLR in R 

examdata = read.csv(file.choose(), header = TRUE)


# By default, the term and format variables are stored as characters.
# In order to use these two variables as categorical variables, we need
# to convert their type to factor. The following two lines do just that. 
Term <- as.factor(examdata$Term)
Format <- as.factor(examdata$Format)

# Store the midterm and final columns of the exam data set in their own vectors 
# in order to keep later code a bit more organized
Midterm <- examdata$Midterm
Final <- examdata$Final

# View the data with a scatterplot matrix using pairs(y~x1+x2+...+xk)
pairs(Final~Midterm+Term+Format, col = "darkblue", lower.panel = NULL)

# The categorical variables will be better understood looking at a boxplot. 
# Create side by side boxplot for Final versus Term   boxplot(y~x)
# Create side by side boxplot for Final versus Format boxplot(y~x)

boxplot(Final~Term, col = blues9)
boxplot(Final~Format, col = blues9)

# Fit a model that has Format, Term and Midterm to help predict Final

mod = lm(Final~Midterm+Term+Format)
summary(mod)

# If you would like to look at a plot of the residuals, you can do so
# with the following code. 
plot(mod, 1) 

 
# Calculate the confidence intervals for each explanatory variable coefficient by hand or 
# with with confint(modelname). 
confint(mod, level = 0.95)

