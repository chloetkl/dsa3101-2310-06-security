## Change Proportion Incidents by Incident Type

## TO MODIFY: 
sec_data_filepath <- "security_data_updated.csv"
desired_ratios <- c(
  "CASES OF EMERGENCY" = 0.1,
  "DAMAGED PROPERTIES" = 0.3,
  "LOST AND FOUND" = 0.4,
  "SEXUAL INCIDENT REPORTS" = 0.05,
  "STOLEN ITEMS" = 0.15
)

library(tidyverse)
security_data <- read.csv(sec_data_filepath) %>% 
  as_tibble()

## current ratios (View Summary)
security_data %>% 
  mutate(Crime = toupper(Crime)) %>% 
  group_by(Crime) %>% summarise(n = n(), .groups="drop") %>% 
  mutate(prop = n/sum(n))

## generate new crimes columns based on desired_ratio
new_crimes <- rep(names(desired_ratios),
                  times=nrow(security_data)*desired_ratios) %>% 
  sample()

security_data <- security_data %>% 
  mutate(Crime= new_crimes)

write.csv(security_data, sec_data_filepath ,row.names = FALSE)


