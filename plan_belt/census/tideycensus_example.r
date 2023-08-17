#install.packages("tidycensus")
library(tidycensus)
library(dplyr)
library(stringr)

# https://cran.r-project.org/web/packages/tidycensus/tidycensus.pdf 

census_api_key("YOUR_KEY") 

# variables
 
v15 <- load_variables(2015, "acs5", cache = TRUE)
View(v15)

v20 <- load_variables(2020, "acs5", cache = TRUE)
View(v20)

# ways to filter

v20 %>% filter(str_detect(name, "B03002")) %>% View()

v20 %>% filter(label == "Estimate!!Total:!!Female:") %>% View()

v20 %>% filter(concept == "SEX BY AGE") %>% View()

# get_acs

# example 1:

?get_acs

mont <- get_acs(geography = "tract", variables = c("B01001_001","B01001_002"),
                state = "PA", county = "montgomery", geometry = FALSE, year = 2020)


# example 2: (wide)

mont_2 <- get_acs(geography = "tract",
  variables = c(not_hispanic = "B03002_002",
                hispanic = "B03002_012"),
  output = "wide",  
  state = "PA", county = c("montgomery","philadelphia"), geometry = TRUE, year = 2020)

plot(mont_2$geometry)
#plot(mont_2)
