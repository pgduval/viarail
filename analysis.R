library(ggplot2)
library(dplyr)
library(grid)
library(gridExtra)

install.packages(c("grid", "gridExtra"))

setwd('/home/elmaster/scraper/viarail')
data = read.csv('./price.csv', stringsAsFactor=FALSE)

head(data)
head(data2)

# clean data
data2 = data %>%
        mutate(date=as.Date(date),
               escape = ifelse(escape=='Sold out', NA, as.numeric(escape)),
               economy = ifelse(economy=='Sold out', NA, as.numeric(economy)),
               economy_plus = ifelse(economy_plus=='Sold out', NA, as.numeric(economy_plus)),
               business = ifelse(business=='Sold out', NA, as.numeric(business)),
               business_plus = ifelse(business_plus=='Sold out', NA, as.numeric(business_plus))       
               )

# summarize
data3 = data2 %>%
        group_by(date, time_departure) %>%
        summarize(escape = mean(escape, na.rm=TRUE),
                  economy = mean(economy, na.rm=TRUE),
                  economy_plus = mean(economy_plus, na.rm=TRUE),
                  business = mean(business, na.rm=TRUE),
                  business_plus = mean(business_plus, na.rm=TRUE)
                  ) %>%
        ungroup()
head(data3)

add_credits = function() {
  grid.text("ddata.com",
            x = 0.99,
            y = 0.02,
            just = "right",
            gp = gpar(fontsize = 12, col = "#777777"))
}

title_with_subtitle = function(title, subtitle = "") {
  ggtitle(bquote(atop(.(title), atop(.(subtitle)))))
}

theme_custom = function(base_size = 12) {
  bg_color = "#f4f4f4"
  bg_rect = element_rect(fill = bg_color, color = bg_color)

  theme_bw(base_size) +
    theme(plot.background = bg_rect,
          panel.background = bg_rect,
          legend.background = bg_rect,
          panel.grid.major = element_line(colour = "grey80", size = 0.25),
          panel.grid.minor = element_line(colour = "grey90", size = 0.25))
}

# Get weekends for plotting
all_dates = seq.Date(from=min(data2$date), to=(max(data2$date)), by='day')
all_weekdays = weekdays(all_dates, abbr = TRUE)
weekends = all_dates[grepl("S(at|un)", all_weekdays)]

w = 640
h = 420
graph_price = function(price){
    # png(filename = "./graph.png", height = h, width = w)
    ggplot(data=data2, aes_string(x='date', y=price, col='scrape_date')) +
        facet_grid(time_departure ~ .) +
        geom_line() +
        geom_vline(xintercept = as.numeric(weekends), linetype=4, col='firebrick3') +
        scale_colour_brewer() + 
        xlab("Days") + ylab(as.character(price)) +
        ggtitle("Price over time") +
        theme_custom(base_size = 16) 
        # add_credits()   
    # dev.off() 
}



graph_price_summary = function(price){
    
    ggplot(data=data3, aes_string(x='date', y=price)) +
        facet_grid(time_departure ~ .) +
        geom_line() +
        geom_vline(xintercept = as.numeric(weekends), linetype=4, col='firebrick3') +
        xlab("Days") + ylab(as.character(price)) +
        ggtitle("Price over time")    

}

graph_price(price='escape')
graph_price(price='economy')
graph_price(price='economy_plus')
graph_price(price='business')
graph_price(price='business_plus')

graph_price_summary(price='escape')
graph_price_summary(price='economy')
graph_price_summary(price='economy_plus')
graph_price_summary(price='business')
graph_price_summary(price='business_plus')

# end
