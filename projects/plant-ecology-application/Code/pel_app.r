# Datasets: 
# og_woody_long - Plant Ecology Data Collected via Plant Ecology Lab
# wi_taxa - Wisconsin Plant Taxonomy
# location_data - Observed Plant Location by Species in Wisconsin

library(shiny)
library(shinydashboard)
library(ggplot2)
library(dplyr)
library(corrplot)
library(shinycssloaders)
library(leaflet)
library(collapsibleTree)
library(mgcv)
library(randomForest)

ui <- dashboardPage(
  skin = "green",
  dashboardHeader(title = "Wisconsin Plant Ecology Application", titleWidth = 350),
  dashboardSidebar(width = 350,
                   sidebarMenu(
                     menuItem("Home", tabName = "home", icon = icon("home")),
                     menuItem("Species Map", tabName = "map", icon = icon("map")),
                     menuItem("Species Dendrogram", tabName = "tree", icon = icon("tree")),
                     menuItem("Species Information", tabName = "species_info", icon = icon("book")),
                     menuItem("Environmental Variable Visualization", tabName = "predictions", icon = icon("chart-bar")),
                     menuItem("Environmental Variable Prediction", tabName = "ml_predictions", icon = icon("cogs")),
                     menuItem("Environmental Variable Correlation Matrix", tabName = "correlation", icon = icon("table")),
                     menuItem("Source Code", tabName="source_code",icon=icon("code")),
                     menuItem("References", tabName="reference_page", icon=icon("file"))
                   )
  ),
  dashboardBody(
    tabItems(
      tabItem(tabName = "home",
              h2("Overview"),
              p("Welcome to the Wisconsin Plant Ecology Application, built by Jackson Cramer in collaboration with Sam Anderson and Kate McCulloh of the UW-Madison Department of Botany's McCulloh Lab. The application is an active project focused on creating a space for ecologists and students that combines principles of ecology and data science to explore and understand the flora of Wisconsin, ecological distributions of species, and the data collected by previous generations of Wisconsin ecologists."),
              h2("Data Background"),
              p("The first extensive efforts to collect plant community ecology data in Wisconsin began in the late 1940s and early 1950s, led by J.T. Curtis and colleagues in the UW-Madison Botany Department at the Wisconsin Plant Ecology Laboratory. They conducted surveys of over 2,000 sites to investigate how plant communities change across different environmental gradients. These sites included diverse ecosystems, such as upland and lowland forests, prairies, savannas, meadows, sand barrens, dunes, fens, and bogs. Subsequent researchers at the Plant Ecology Laboratory have resurveyed over 500 of these original sites, approximating the initial locations due to unmarked quadrats, and using either the original or more rigorous sampling protocols. Both the original and resurveyed data is included within this application."),
              tabItem(tabName = "info",
                      h2("Environmental Variable Definitions"),
                      tags$ul(
                        style = "list-style-position: inside; padding-left: 0; margin-left: 0;",  # Remove indentation
                        tags$li("CI – Continuum Index, ranging from 300-3000"),
                        tags$li("trees.acre - # of trees per acre"),
                        tags$li("BA.acre – Basal area (in sq. inches) of trees per acre"),
                        tags$li("pH – soil pH"),
                        tags$li("CA – Soil Calcium in ppm"),
                        tags$li("MG – Soil Magnesium in ppm"),
                        tags$li("P – Soil Phosphorus in ppm"),
                        tags$li("K – Soil Potassium in ppm"),
                        tags$li("NO3 – Soil Nitrate in ppm"),
                        tags$li("percent_freq – percent frequency")
                      ))
      ),
      tabItem(tabName = "tree",
              h2("Wisconsin Flora Interactive Dendrogram"),
              h4("Click Nodes to Further Explore Dendrogram (Family -> Genus -> Species)"),
              collapsibleTreeOutput('tree', height='700px') %>% withSpinner(color = "green")
      ),
      tabItem(tabName = "map",
              h2("Species Location Map"),
              h4("Species Presence by Frequency"),
              sidebarLayout(
                sidebarPanel(
                  selectInput("map_year", "Select Year:", choices = c("select" = ""), selected = ""),
                  selectInput("map_species", "Select Species:", choices = c("select" = ""), selected = "", multiple = TRUE)
                ),
                mainPanel(
                  leafletOutput("speciesMap", height = 600) %>% withSpinner(color = "green"),
                )
              )
      ),
      tabItem(tabName = "predictions",
              h2("Visualize the Relationship Between Environmental Variables"),
              sidebarLayout(
                sidebarPanel(
                  selectInput("pred_xvar", "Select X Variable:", choices = c("select" = ""), selected = ""),
                  selectInput("pred_yvar", "Select Y Variable:", choices = c("select" = ""), selected = "")
                ),
                mainPanel(
                  fluidRow(
                    column(6, plotOutput("pred_plot") %>% withSpinner(color = "green")),
                    column(6, plotOutput("gam_plot") %>% withSpinner(color = "green"))
                  )
                )
              )
      ),
      tabItem(tabName = "correlation",
              h2("Environmental Variable Correlation Matrix"),
              sidebarLayout(
                sidebarPanel(
                  selectInput("correlation_vars", "Select Variables:", choices = c("select" = ""), selected = "", multiple = TRUE)
                ),
                mainPanel(
                  plotOutput("correlationPlot") %>% withSpinner(color = "green")
                )
              )
      ),
      tabItem(tabName = "species_info",
              h2("Species Information"),
              tags$iframe(src = "https://wisflora.herbarium.wisc.edu/index.php",
                          style = "border:none; width: 100%; height: 800px;")
      ),
      tabItem(tabName = "source_code",
              h2("Source Code of Wisconsin Plant Ecology Application"),
              verbatimTextOutput("source_code_output")
      ),
      tabItem(tabName = "reference_page",
              h2("References"),
              tags$div(
                style = "padding-left: 1em; text-indent: -1em;",
                
                tags$p("Amatangelo, K. L., Fulton, M. R., Rogers, D. A., & Waller, D. M. (2011). Converging forest community composition along an edaphic gradient threatens landscape-level diversity. ", 
                       tags$i("Diversity and Distributions"), ", 17(2), 201–213. ", 
                       tags$a(href = "https://doi.org/10.1111/j.1472-4642.2010.00730.x", "https://doi.org/10.1111/j.1472-4642.2010.00730.x")),
                
                tags$p("Beck, J. J., & Richards, J. H. (2023). Functional traits influence local plant distributions and spatial patterns of diversity within a heterogeneous bedrock glade. ", 
                       tags$i("Plant Ecology"), ", 224(8), 729–740. ", 
                       tags$a(href = "https://doi.org/10.1007/s11258-023-01337-x", "https://doi.org/10.1007/s11258-023-01337-x")),
                
                tags$p("Bohman, A., Buckler, D., Clark, F., Dallman, M., Eckstein, R., Handler, S., Holmes, J., Hutnik, B., Larson, L., Parker, L., & Rideout, D. (2021). W ICCI Forestry Working Group: Progress and Emerging Opportunities. Wisconsin Initiative on Climate Change Impacts."),
                
                tags$p("Hanberry, B. B., & Dey, D. C. (2019). Historical range of variability for restoration and management in Wisconsin. ", 
                       tags$i("Biodiversity and Conservation"), ", 28(11), 2931–2950. ", 
                       tags$a(href = "https://doi.org/10.1007/s10531-019-01806-8", "https://doi.org/10.1007/s10531-019-01806-8")),
                
                tags$p("Li, D., & Waller, D. (2016). Long-term shifts in the patterns and underlying processes of plant associations in Wisconsin forests. ", 
                       tags$i("Global Ecology and Biogeography"), ", 25(5), 516–526. ", 
                       tags$a(href = "https://doi.org/10.1111/geb.12432", "https://doi.org/10.1111/geb.12432")),
                
                tags$p("Rogers, D. A., Rooney, T. P., Olson, D., & Waller, D. M. (2008). Shifts in Southern Wisconsin forest canopy and understory richness, composition, and heterogeneity. ", 
                       tags$i("Ecology"), ", 89(9). ", 
                       tags$a(href = "https://doi.org/10.1890/07-1129.1", "https://doi.org/10.1890/07-1129.1")),
                
                tags$p("Waller, D., Amatangelo, K., Johnson, S., & Rogers, D. (2013). Wisconsin Vegetation Database – plant community survey and resurvey data from the Wisconsin Plant Ecology Laboratory. ", 
                       tags$i("Biodiversity & Ecology"), ", 4, 255–264. ", 
                       tags$a(href = "https://doi.org/10.7809/b-e.00082", "https://doi.org/10.7809/b-e.00082")),
                
                tags$p("Wiegmann, S. M., & Waller, D. M. (2006). Fifty years of change in northern upland forest understories: Identity and traits of “winner” and “loser” plant species. ", 
                       tags$i("Biological Conservation"), ", 129(1). ", 
                       tags$a(href = "https://doi.org/10.1016/j.biocon.2005.10.027", "https://doi.org/10.1016/j.biocon.2005.10.027"))
              )
      )
      
      ,
      tabItem(tabName = "ml_predictions",
              h2("Environmental Variable Prediction via Random Forest Algorithm"),
              sidebarLayout(
                sidebarPanel(
                  selectInput("ml_target", "Select Target Variable:", choices = c("select" = ""), selected = ""),
                  selectInput("ml_features", "Select Feature Variables:", choices = c("select" = ""), selected = "", multiple = TRUE),
                  uiOutput("feature_inputs")
                ),
                mainPanel(
                  verbatimTextOutput("ml_prediction_output")
                )
              )
      )
    )
  )
)

server <- function(input, output, session) {
  output$source_code_output <- renderText({
    # Ensure the file path is correct; update if needed
    file_path <- path_to_source_code
    code_lines <- readLines(file_path)
    paste(code_lines, collapse = "\n")
  }) 
  
  dataset <- reactive({ og_woody_long })
  
  
  observe({
    numeric_vars <- names(dataset())[sapply(dataset(), is.numeric)]
    updateSelectInput(session, "pred_xvar", choices = c("select" = "", numeric_vars), selected = "")
    updateSelectInput(session, "pred_yvar", choices = c("select" = "", numeric_vars), selected = "")
    updateSelectInput(session, "correlation_vars", choices = c("select" = "", numeric_vars), selected = "")
    updateSelectInput(session, "ml_target", choices = c("select" = "", numeric_vars), selected = "")
    updateSelectInput(session, "ml_features", choices = c("select" = "", numeric_vars), selected = "")
  })
  
  
  output$feature_inputs <- renderUI({
    req(input$ml_features)
    lapply(input$ml_features, function(feature) {
      numericInput(inputId = paste0("feature_", feature), 
                   label = paste("Select Value for", feature),
                   value = 0
      )
    })
  })
  
  
  output$ml_prediction_output <- renderText({
    req(input$ml_target, input$ml_features)
    
    feature_values <- sapply(input$ml_features, function(feature) input[[paste0("feature_", feature)]])
    
    if (all(!is.na(feature_values) & feature_values != "")) {
      model_data <- dataset() %>%
        select(all_of(c(input$ml_target, input$ml_features))) %>%
        na.omit()
      
      formula <- as.formula(paste(input$ml_target, "~", paste(input$ml_features, collapse = "+")))
      rf_model <- randomForest(formula, data = model_data, ntree = 100, maxnodes=10)
      
      prediction_data <- as.data.frame(as.list(feature_values))
      colnames(prediction_data) <- input$ml_features
      
      prediction <- predict(rf_model, newdata = prediction_data)
      
      paste("Predicted", input$ml_target, ":", round(prediction, 2))
    } else {
      "Please enter values for all selected features to see the prediction."
    }
  })
  
  
  output$tree <- renderCollapsibleTree({
    req(wi_taxa)
    
    tree_data <- wi_taxa %>%
      mutate(First_Letter_Family = substr(Family, 1, 1)) %>%
      group_by(First_Letter_Family, Family, Genus, Full.Name) %>%
      summarise(count = n(), .groups = 'drop') %>%
      as.data.frame()
    
    collapsibleTree(
      tree_data,
      hierarchy = c("First_Letter_Family", "Family", "Genus", "Full.Name"),
      root = "Click First Letter of Family",
      zoomable = TRUE,
      width = 800,
      height = 600,
      nodeColour = "#69b3a2",
      edgeColour = "#b2b2b2"
    )
  })
  
  observe({
    req(location_data)
    years <- unique(location_data$year)
    species_list <- unique(location_data$Species)
    
    updateSelectInput(session, "map_year", choices = c("select" = "", years), selected = "")
    updateSelectInput(session, "map_species", choices = c("select" = "", species_list), selected = "")
  })
  
  output$speciesMap <- renderLeaflet({
    req(input$map_year, input$map_species)
    
    map_data <- location_data %>%
      filter(year == input$map_year, Species %in% input$map_species)
    
    species_colors <- colorFactor(rainbow(length(unique(map_data$Species))), map_data$Species)
    circle_radius <- map_data$Frequency / max(map_data$Frequency, na.rm = TRUE) * 10
    
    leaflet(map_data) %>%
      addTiles() %>%
      addCircleMarkers(~LONG, ~LAT, color = ~species_colors(Species), fill = TRUE,
                       radius = circle_radius, fillOpacity = 0.7) %>%
      addLegend("bottomright", pal = species_colors, values = ~Species,
                title = "Species", opacity = 1)
  })
  
  output$pred_plot <- renderPlot({
    req(input$pred_xvar, input$pred_yvar)
    
    pred_data <- dataset() %>%
      filter(!is.na(.data[[input$pred_xvar]]) & !is.na(.data[[input$pred_yvar]]))
    
    ggplot(pred_data, aes_string(x = input$pred_xvar, y = input$pred_yvar)) +
      geom_point() +
      geom_smooth(method = "lm", color = "blue", se = FALSE) +
      labs(title = paste("Linear Regression of", input$pred_yvar, "vs", input$pred_xvar))
  })
  
  output$gam_plot <- renderPlot({
    req(input$pred_xvar, input$pred_yvar)
    
    gam_data <- dataset() %>%
      filter(!is.na(.data[[input$pred_xvar]]) & !is.na(.data[[input$pred_yvar]]))
    
    gam_model <- gam(as.formula(paste(input$pred_yvar, "~ s(", input$pred_xvar, ")")), data = gam_data)
    
    ggplot(gam_data, aes_string(x = input$pred_xvar, y = input$pred_yvar)) +
      geom_point() +
      geom_smooth(method = "gam", formula = y ~ s(x), color = "darkgreen", se = FALSE) +
      labs(title = paste("Generalized Additive Model of", input$pred_yvar, "vs", input$pred_xvar))
  })
  
  output$correlationPlot <- renderPlot({
    req(input$correlation_vars)
    
    if (length(input$correlation_vars) < 2) {
      plot.new()
      text(0.5, 0.5, "Please select at least two variables to generate a correlation matrix.", cex = 1.5)
    } else {
      corr_data <- dataset() %>%
        select(all_of(input$correlation_vars)) %>%
        na.omit()
      
      corr_matrix <- cor(corr_data)
      corrplot(corr_matrix, method = "circle", type = "upper", tl.col = "black", tl.srt = 45)
    }
  })
  
}

shinyApp(ui, server)
