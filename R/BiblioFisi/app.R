library(shiny)
library(bibliometrix)
library(DT)
library(ggplot2)
library(shinythemes)
library(dplyr)
library(plotly)

# Interfaz de usuario
ui <- fluidPage(
  theme = shinytheme("flatly"),  # Cambia a un tema más moderno
  titlePanel(tags$h2("Visualización de Tesis y Trabajos", style = "color: #2c3e50; font-weight: bold;")),
  
  sidebarLayout(
    sidebarPanel(
      fileInput("file", "Subir archivo CSV", accept = ".csv"),
      checkboxInput("showTable", "Mostrar tabla de datos", TRUE),
      selectInput("field", "Seleccionar campo para análisis gráfico",
                  choices = c("Autores" = "Autores",
                              "Palabras clave" = "Palabras clave",
                              "Fecha de publicación" = "Fecha de publicación")),
      sliderInput("topN", "Seleccionar número de elementos a mostrar", min = 5, max = 20, value = 10, step = 1),
      actionButton("plotBtn", "Generar gráficos", class = "btn-primary"),
      hr(),
      helpText("Sube un archivo CSV con datos de tesis o trabajos para explorar la información.")
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel(
          "Tabla",
          conditionalPanel(
            condition = "input.showTable == true",
            DTOutput("table")
          )
        ),
        tabPanel(
          "Gráficos",
          fluidRow(
            column(6, plotlyOutput("barPlot", height = "400px")),
            column(6, plotlyOutput("pieChart", height = "400px"))
          ),
          hr(),
          fluidRow(
            column(12, plotOutput("timePlot", height = "400px"))
          )
        )
      )
    )
  )
)

# Lógica del servidor
server <- function(input, output, session) {
  
  # Cargar datos
  data <- reactive({
    req(input$file)
    read.csv(input$file$datapath, header = TRUE, sep = ";")
  })
  
  # Renderizar tabla estilizada
  output$table <- renderDT({
    req(data())
    datatable(
      data() %>% 
        mutate(
          Título = paste0('<details><summary>Ver</summary>', Título, '</details>'),
          Resumen = paste0('<details><summary>Ver</summary>', Resumen, '</details>')
        ),
      escape = FALSE,
      options = list(
        pageLength = 5,
        autoWidth = TRUE,
        columnDefs = list(
          list(width = '300px', targets = c(1, 6))
        )
      ),
      style = "bootstrap",
      class = "table table-hover table-striped"
    )
  })
  
  # Generar gráfico de barras
  output$barPlot <- renderPlotly({
    req(data(), input$field, input$plotBtn)
    
    # Filtrar y procesar datos
    selected_field <- switch(input$field,
                             "Autores" = data()$Autores,
                             "Palabras clave" = data()$Palabras.clave,
                             "Fecha de publicación" = data()$Fecha.de.publicación)
    counts <- table(unlist(strsplit(as.character(selected_field), ",|;")))
    df <- data.frame(Term = names(counts), Count = as.numeric(counts))
    df <- df[order(-df$Count), ][1:input$topN, ]
    
    # Crear gráfico interactivo
    plot_ly(
      data = df,
      x = ~Count, y = ~reorder(Term, Count),
      type = "bar", orientation = "h",
      marker = list(color = "#1f78b4"),
      hoverinfo = "x+y"
    ) %>% layout(
      title = paste("Top", input$topN, input$field),
      xaxis = list(title = "Frecuencia"),
      yaxis = list(title = input$field),
      margin = list(l = 150)
    )
  })
  
  # Generar gráfico de pastel
  output$pieChart <- renderPlotly({
    req(data(), input$field, input$plotBtn)
    
    selected_field <- switch(input$field,
                             "Autores" = data()$Autores,
                             "Palabras clave" = data()$Palabras.clave,
                             "Fecha de publicación" = data()$Fecha.de.publicación)
    counts <- table(unlist(strsplit(as.character(selected_field), ",|;")))
    df <- data.frame(Term = names(counts), Count = as.numeric(counts))
    df <- df[order(-df$Count), ][1:input$topN, ]
    
    plot_ly(
      data = df,
      labels = ~Term, values = ~Count,
      type = "pie",
      textinfo = "label+percent",
      insidetextorientation = "radial",
      marker = list(colors = RColorBrewer::brewer.pal(8, "Set3"))
    ) %>% layout(
      title = paste("Distribución de", input$field),
      margin = list(t = 50, b = 50)
    )
  })
  
  # Generar gráfico de tendencias (Fecha de publicación)
  output$timePlot <- renderPlot({
    req(data(), input$plotBtn, input$field == "Fecha de publicación")
    
    df <- data() %>%
      count(Fecha.de.publicación) %>%
      arrange(Fecha.de.publicación)
    
    ggplot(df, aes(x = as.integer(Fecha.de.publicación), y = n)) +
      geom_line(color = "#2c3e50", size = 1) +
      geom_point(color = "#e74c3c", size = 3) +
      labs(title = "Tendencia de publicaciones por año",
           x = "Año", y = "Cantidad de publicaciones") +
      theme_minimal() +
      theme(
        plot.title = element_text(hjust = 0.5, size = 18, face = "bold"),
        axis.text = element_text(size = 12),
        axis.title = element_text(size = 14)
      )
  })
}

# Lanzar la aplicación
shinyApp(ui, server)
