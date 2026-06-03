Imports System.Drawing
Imports System.Drawing.Drawing2D
Imports System.Windows.Forms

Public Class Form1

    ' ================= CORE ENGINE =================
    Private WithEvents FrameTimer As New Windows.Forms.Timer()
    Private intersections As New List(Of CityIntersection)

    ' Environment Detail Objects (Cached to avoid flickering/regeneration)
    Private houseRects As New List(Of Rectangle)
    Private houseColors As New List(Of Color)
    Private houseRidgeColors As New List(Of Color)
    Private treePoints As New List(Of Point)

    ' ================= INITIALIZATION =================
    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Me.DoubleBuffered = True
        Me.Width = 1024
        Me.Height = 1024
        Me.Text = "Smart Synchronized Metropolitan Traffic System"
        Me.BackColor = Color.FromArgb(55, 125, 70)

        ' 4 Intersections arranged cleanly in a perfect square top-view layout
        intersections.Add(New CityIntersection(170, 170, 0))    ' Top-Left Node
        intersections.Add(New CityIntersection(570, 170, 80))   ' Top-Right Node
        intersections.Add(New CityIntersection(170, 570, 80))   ' Bottom-Left Node
        intersections.Add(New CityIntersection(570, 570, 0))    ' Bottom-Right Node

        GenerateCityEnvironment()

        FrameTimer.Interval = 30
        FrameTimer.Start()
    End Sub

    Private Sub GenerateCityEnvironment()
        Dim rand As New Random(777)

        Dim buildZones As New List(Of Rectangle) From {
            New Rectangle(30, 30, 110, 110),
            New Rectangle(340, 30, 200, 110),
            New Rectangle(740, 30, 240, 110),
            New Rectangle(30, 340, 110, 200),
            New Rectangle(740, 340, 240, 200),
            New Rectangle(30, 740, 110, 240),
            New Rectangle(340, 740, 200, 240),
            New Rectangle(740, 740, 240, 240)
        }

        For Each zone As Rectangle In buildZones
            Dim attempts As Integer = zone.Width \ 40
            Dim zoneHouses As New List(Of Rectangle)()

            ' 1. Generate and place houses safely
            For i As Integer = 0 To attempts - 1
                Dim hW As Integer = rand.Next(40, 50)
                Dim hH As Integer = rand.Next(40, 50)
                Dim hX As Integer = zone.X + (i * 55) + rand.Next(0, 5)
                Dim hY As Integer = zone.Y + rand.Next(0, zone.Height - hH)

                Dim targetHouseRect As New Rectangle(hX, hY, hW, hH)
                If zone.Contains(targetHouseRect) Then
                    houseRects.Add(targetHouseRect)
                    zoneHouses.Add(targetHouseRect)

                    Dim colorPick As Integer = rand.Next(0, 3)
                    If colorPick = 0 Then
                        houseColors.Add(Color.FromArgb(195, 85, 60))
                        houseRidgeColors.Add(Color.FromArgb(125, 40, 20))
                    ElseIf colorPick = 1 Then
                        houseColors.Add(Color.FromArgb(65, 100, 135))
                        houseRidgeColors.Add(Color.FromArgb(30, 50, 75))
                    Else
                        houseColors.Add(Color.FromArgb(100, 105, 110))
                        houseRidgeColors.Add(Color.FromArgb(55, 60, 65))
                    End If
                End If
            Next

            ' 2. Generate trees safely
            Dim tPlaced As Integer = 0
            While tPlaced < 4
                Dim tx As Integer = rand.Next(zone.X + 5, zone.X + zone.Width - 20)
                Dim ty As Integer = rand.Next(zone.Y + 5, zone.Y + zone.Height - 20)
                Dim treeCheckRect As New Rectangle(tx, ty, 24, 24)

                Dim hitsHouse As Boolean = False
                For Each hRect As Rectangle In zoneHouses
                    If hRect.IntersectsWith(treeCheckRect) Then
                        hitsHouse = True
                        Exit For
                    End If
                Next

                If Not hitsHouse Then
                    treePoints.Add(New Point(tx, ty))
                    tPlaced += 1
                End If
            End While
        Next zone
    End Sub

    ' ================= ENGINE LOOP =================
    Private Sub FrameTimer_Tick(sender As Object, e As EventArgs) Handles FrameTimer.Tick
        For Each intersection As CityIntersection In intersections
            intersection.Update()
        Next
        Me.Invalidate()
    End Sub

    ' ================= RENDERING PIPELINE =================
    Private Sub Form1_Paint(sender As Object, e As PaintEventArgs) Handles MyBase.Paint
        Dim g As Graphics = e.Graphics
        g.SmoothingMode = SmoothingMode.AntiAlias

        DrawGrassTerrainLayout(g)
        DrawAsphaltRoadNetwork(g)
        DrawDecorativeCityAssets(g)
        DrawCentralPlazaPark(g)

        ' Draw active localized intersection systems
        For Each intersection As CityIntersection In intersections
            intersection.Draw(g)
        Next
    End Sub

    Private Sub DrawGrassTerrainLayout(g As Graphics)
        Using grassBrush As New HatchBrush(HatchStyle.Percent05, Color.FromArgb(48, 115, 62), Color.FromArgb(55, 125, 70))
            g.FillRectangle(grassBrush, 0, 0, Width, Height)
        End Using
    End Sub

    Private Sub DrawAsphaltRoadNetwork(g As Graphics)
        Dim asphaltColor As Color = Color.FromArgb(45, 45, 48)
        Dim sidewalkColor As Color = Color.FromArgb(165, 165, 165)
        Dim curbColor As Color = Color.FromArgb(130, 130, 135)
        Dim jointColor As Color = Color.FromArgb(150, 150, 155)

        Using asphalt As New SolidBrush(asphaltColor),
              sidewalk As New SolidBrush(sidewalkColor),
              curbPen As New Pen(curbColor, 2),
              jointPen As New Pen(jointColor, 1),
              laneYellow As New Pen(Color.FromArgb(235, 180, 50), 3),
              laneWhite As New Pen(Color.FromArgb(210, 210, 215), 2)

            laneWhite.DashStyle = DashStyle.Dash
            jointPen.DashStyle = DashStyle.Dash

            ' Horizontal Highway 1 (Y = 170)
            g.FillRectangle(sidewalk, 0, 170 - 20, Width, 180)
            g.FillRectangle(asphalt, 0, 170, Width, 140)
            g.DrawLine(jointPen, 0, 170 - 10, Width, 170 - 10)
            g.DrawLine(jointPen, 0, 170 + 150, Width, 170 + 150)
            g.DrawLine(curbPen, 0, 170, Width, 170)
            g.DrawLine(curbPen, 0, 170 + 140, Width, 170 + 140)
            g.DrawLine(laneYellow, 0, 170 + 68, Width, 170 + 68)
            g.DrawLine(laneYellow, 0, 170 + 72, Width, 170 + 72)
            g.DrawLine(laneWhite, 0, 170 + 35, Width, 170 + 35)
            g.DrawLine(laneWhite, 0, 170 + 105, Width, 170 + 105)

            ' Horizontal Highway 2 (Y = 570)
            g.FillRectangle(sidewalk, 0, 570 - 20, Width, 180)
            g.FillRectangle(asphalt, 0, 570, Width, 140)
            g.DrawLine(jointPen, 0, 570 - 10, Width, 570 - 10)
            g.DrawLine(jointPen, 0, 570 + 150, Width, 570 + 150)
            g.DrawLine(curbPen, 0, 570, Width, 570)
            g.DrawLine(curbPen, 0, 570 + 140, Width, 570 + 140)
            g.DrawLine(laneYellow, 0, 570 + 68, Width, 570 + 68)
            g.DrawLine(laneYellow, 0, 570 + 72, Width, 570 + 72)
            g.DrawLine(laneWhite, 0, 570 + 35, Width, 570 + 35)
            g.DrawLine(laneWhite, 0, 570 + 105, Width, 570 + 105)

            ' Vertical Avenue 1 (X = 170)
            g.FillRectangle(sidewalk, 170 - 20, 0, 180, Height)
            g.FillRectangle(asphalt, 170, 0, 140, Height)
            g.DrawLine(jointPen, 170 - 10, 0, 170 - 10, Height)
            g.DrawLine(jointPen, 170 + 150, 0, 170 + 150, Height)
            g.DrawLine(curbPen, 170, 0, 170, Height)
            g.DrawLine(curbPen, 170 + 140, 0, 170 + 140, Height)
            g.DrawLine(laneYellow, 170 + 68, 0, 170 + 68, Height)
            g.DrawLine(laneYellow, 170 + 72, 0, 170 + 72, Height)
            g.DrawLine(laneWhite, 170 + 35, 0, 170 + 35, Height)
            g.DrawLine(laneWhite, 170 + 105, 0, 170 + 105, Height)

            ' Vertical Avenue 2 (X = 570)
            g.FillRectangle(sidewalk, 570 - 20, 0, 180, Height)
            g.FillRectangle(asphalt, 570, 0, 140, Height)
            g.DrawLine(jointPen, 570 - 10, 0, 570 - 10, Height)
            g.DrawLine(jointPen, 570 + 150, 0, 570 + 150, Height)
            g.DrawLine(curbPen, 570, 0, 570, Height)
            g.DrawLine(curbPen, 570 + 140, 0, 570 + 140, Height)
            g.DrawLine(laneYellow, 570 + 68, 0, 570 + 68, Height)
            g.DrawLine(laneYellow, 570 + 72, 0, 570 + 72, Height)
            g.DrawLine(laneWhite, 570 + 35, 0, 570 + 35, Height)
            g.DrawLine(laneWhite, 570 + 105, 0, 570 + 105, Height)

        End Using
    End Sub

    Private Sub DrawDecorativeCityAssets(g As Graphics)
        For i As Integer = 0 To houseRects.Count - 1
            Dim rect As Rectangle = houseRects(i)
            Using roofBrush As New SolidBrush(houseColors(i)),
                  ridgeBrush As New SolidBrush(houseRidgeColors(i)),
                  shadowBrush As New SolidBrush(Color.FromArgb(45, 0, 0, 0)),
                  chimneyBrush As New SolidBrush(Color.FromArgb(80, 80, 85))

                g.FillRectangle(shadowBrush, rect.X + 6, rect.Y + 6, rect.Width, rect.Height)
                g.FillRectangle(Brushes.WhiteSmoke, rect)
                g.DrawRectangle(Pens.Black, rect)

                Dim roofInner As New Rectangle(rect.X + 3, rect.Y + 3, rect.Width - 6, rect.Height - 6)
                g.FillRectangle(roofBrush, roofInner)
                g.DrawRectangle(Pens.DarkSlateGray, roofInner)

                Dim ridgeWidth As Integer = roofInner.Width - 12
                Dim ridgeRect As New Rectangle(roofInner.X + 6, roofInner.Y + (roofInner.Height \ 2) - 3, ridgeWidth, 6)
                g.FillRectangle(ridgeBrush, ridgeRect)

                g.DrawLine(Pens.Black, roofInner.X, roofInner.Y, ridgeRect.X, ridgeRect.Y)
                g.DrawLine(Pens.Black, roofInner.X + roofInner.Width, roofInner.Y, ridgeRect.X + ridgeRect.Width, ridgeRect.Y)
                g.DrawLine(Pens.Black, roofInner.X, roofInner.Y + roofInner.Height, ridgeRect.X, ridgeRect.Y + ridgeRect.Height)
                g.DrawLine(Pens.Black, roofInner.X + roofInner.Width, roofInner.Y + roofInner.Height, ridgeRect.X + ridgeRect.Width, ridgeRect.Y + ridgeWidth)

                g.FillRectangle(shadowBrush, roofInner.X + 8, roofInner.Y + 6, 8, 8)
                g.FillRectangle(chimneyBrush, roofInner.X + 6, roofInner.Y + 4, 8, 8)
                g.DrawRectangle(Pens.Black, roofInner.X + 6, roofInner.Y + 4, 8, 8)
            End Using
        Next i

        For Each pt As Point In treePoints
            Using shadowBrush As New SolidBrush(Color.FromArgb(50, 0, 0, 0)),
                  leavesBrush As New SolidBrush(Color.FromArgb(35, 95, 45)),
                  highlightBrush As New SolidBrush(Color.FromArgb(55, 135, 65))

                g.FillEllipse(shadowBrush, pt.X + 4, pt.Y + 4, 26, 26)
                g.FillEllipse(leavesBrush, pt.X, pt.Y, 26, 26)
                g.FillEllipse(highlightBrush, pt.X + 3, pt.Y + 2, 16, 16)
                g.DrawEllipse(Pens.Black, pt.X, pt.Y, 26, 26)
            End Using
        Next
    End Sub

    Private Sub DrawCentralPlazaPark(g As Graphics)
        Dim xStart As Integer = 310
        Dim xEnd As Integer = 570
        Dim pSize As Integer = xEnd - xStart

        Using grassPlat As New SolidBrush(Color.FromArgb(40, 110, 55)),
              stoneEdge As New Pen(Color.FromArgb(90, 90, 95), 3)
            g.FillRectangle(grassPlat, xStart, xStart, pSize, pSize)
            g.DrawRectangle(stoneEdge, xStart, xStart, pSize, pSize)
        End Using

        Using walkwayBrush As New HatchBrush(HatchStyle.HorizontalBrick, Color.FromArgb(130, 130, 135), Color.FromArgb(160, 160, 165))
            g.FillRectangle(walkwayBrush, xStart, xStart + (pSize \ 2) - 20, pSize, 40)
            g.FillRectangle(walkwayBrush, xStart + (pSize \ 2) - 20, xStart, 40, pSize)
        End Using

        Dim midPoint As Integer = xStart + (pSize \ 2)
        Dim baseW As Integer = 70
        Dim bx As Integer = midPoint - (baseW \ 2)

        Using platformBrush As New SolidBrush(Color.FromArgb(95, 95, 100)),
              borderPen As New Pen(Color.FromArgb(50, 50, 52), 2)
            g.FillRectangle(platformBrush, bx, bx, baseW, baseW)
            g.DrawRectangle(borderPen, bx, bx, baseW, baseW)
        End Using

        Using shadowBrush As New SolidBrush(Color.FromArgb(60, 0, 0, 0)),
              monolithCore As New SolidBrush(Color.FromArgb(190, 195, 200)),
              capstoneBrush As New SolidBrush(Color.FromArgb(140, 145, 150))

            g.FillRectangle(shadowBrush, midPoint - 15 + 6, midPoint - 15 + 6, 30, 30)
            g.FillRectangle(Brushes.DarkGray, midPoint - 20, midPoint - 20, 40, 40)
            g.DrawRectangle(Pens.Black, midPoint - 20, midPoint - 20, 40, 40)

            g.FillRectangle(monolithCore, midPoint - 14, midPoint - 14, 28, 28)
            g.DrawRectangle(Pens.DarkSlateGray, midPoint - 14, midPoint - 14, 28, 28)

            g.FillRectangle(capstoneBrush, midPoint - 8, midPoint - 8, 16, 16)
            g.DrawRectangle(Pens.Black, midPoint - 8, midPoint - 8, 16, 16)
        End Using
    End Sub

    Protected Overrides Sub OnMouseClick(e As MouseEventArgs)
        MyBase.OnMouseClick(e)
        For Each intersection As CityIntersection In intersections
            intersection.CheckButtonClick(e.Location)
        Next
    End Sub

End Class

' ================= DECENTRALIZED SYNCHRONIZED INTERSECTION ZONE =================
Public Class CityIntersection
    Public Property X As Integer
    Public Property Y As Integer
    Private ReadOnly size As Integer = 140

    Private localCycleTimer As Integer = 0
    Private currentPhaseIndex As Integer = 0

    Private nsPedRequested As Boolean = False
    Private ewPedRequested As Boolean = False

    Private nsPedWalkActive As Boolean = False
    Private ewPedWalkActive As Boolean = False
    Private pedTimer As Integer = 0

    Private btnNorthWest, btnNorthEast, btnSouthWest, btnSouthEast As Rectangle

    Public Sub New(x As Integer, y As Integer, startOffsetTicks As Integer)
        Me.X = x
        Me.Y = y
        Me.localCycleTimer = startOffsetTicks

        btnNorthWest = New Rectangle(x - 22, y - 22, 18, 18)
        btnNorthEast = New Rectangle(x + size + 4, y - 22, 18, 18)
        btnSouthWest = New Rectangle(x - 22, y + size + 4, 18, 18)
        btnSouthEast = New Rectangle(x + size + 4, y + size + 4, 18, 18)
    End Sub

    Public Sub Update()
        If nsPedWalkActive Or ewPedWalkActive Then
            pedTimer += 1
            If pedTimer > 120 Then
                nsPedWalkActive = False
                ewPedWalkActive = False
                pedTimer = 0
                localCycleTimer = 0
            End If
            Exit Sub
        End If

        localCycleTimer += 1

        Select Case currentPhaseIndex
            Case 0
                If nsPedRequested AndAlso localCycleTimer > 60 Then
                    currentPhaseIndex = 1
                    localCycleTimer = 0
                ElseIf localCycleTimer > 140 Then
                    currentPhaseIndex = 1
                    localCycleTimer = 0
                End If

            Case 1
                If localCycleTimer > 40 Then
                    If nsPedRequested Then
                        nsPedWalkActive = True
                        nsPedRequested = False
                        localCycleTimer = 0
                    Else
                        currentPhaseIndex = 2
                        localCycleTimer = 0
                    End If
                End If

            Case 2
                If ewPedRequested AndAlso localCycleTimer > 60 Then
                    currentPhaseIndex = 3
                    localCycleTimer = 0
                ElseIf localCycleTimer > 140 Then
                    currentPhaseIndex = 3
                    localCycleTimer = 0
                End If

            Case 3
                If localCycleTimer > 40 Then
                    If ewPedRequested Then
                        ewPedWalkActive = True
                        ewPedRequested = False
                        localCycleTimer = 0
                    Else
                        currentPhaseIndex = 0
                        localCycleTimer = 0
                    End If
                End If
        End Select
    End Sub

    Public Sub CheckButtonClick(mousePt As Point)
        If btnNorthWest.Contains(mousePt) Or btnSouthEast.Contains(mousePt) Then
            nsPedRequested = True
        End If
        If btnNorthEast.Contains(mousePt) Or btnSouthWest.Contains(mousePt) Then
            ewPedRequested = True
        End If
    End Sub

    Public Sub Draw(g As Graphics)
        Using asphaltInter As New SolidBrush(Color.FromArgb(45, 45, 48))
            g.FillRectangle(asphaltInter, X, Y, size, size)
        End Using

        DrawZebraCrosswalkLines(g)

        Dim nsLightState As Integer = 0
        Dim ewLightState As Integer = 0

        If Not nsPedWalkActive AndAlso Not ewPedWalkActive Then
            If currentPhaseIndex = 0 Then nsLightState = 2
            If currentPhaseIndex = 1 Then nsLightState = 1
            If currentPhaseIndex = 2 Then ewLightState = 2
            If currentPhaseIndex = 3 Then ewLightState = 1
        End If

        DrawSystemInfrastructure(g, btnNorthWest, -1, -1, True, nsLightState, nsPedWalkActive)
        DrawSystemInfrastructure(g, btnNorthEast, 1, -1, False, ewLightState, ewPedWalkActive)
        DrawSystemInfrastructure(g, btnSouthWest, -1, 1, False, ewLightState, ewPedWalkActive)
        DrawSystemInfrastructure(g, btnSouthEast, 1, 1, True, nsLightState, nsPedWalkActive)
    End Sub

    Private Sub DrawZebraCrosswalkLines(g As Graphics)
        Using stripeBrush As New SolidBrush(Color.FromArgb(225, 225, 230))
            For i As Integer = 6 To size - 12 Step 16
                g.FillRectangle(stripeBrush, X + i, Y - 12, 8, 12)
                g.FillRectangle(stripeBrush, X + i, Y + size, 8, 12)
                g.FillRectangle(stripeBrush, X - 12, Y + i, 12, 8)
                g.FillRectangle(stripeBrush, X + size, Y + i, 12, 8)
            Next i
        End Using
    End Sub

    ' FIXED: Explicitly typed all parameters here, removing the 'Befores' typo
    Private Sub DrawSystemInfrastructure(g As Graphics, bounds As Rectangle, dirX As Integer, dirY As Integer, isVerticalLight As Boolean, vehicleState As Integer, pedWalkActive As Boolean)
        Dim yellowBase As Color = Color.FromArgb(245, 195, 20)

        Using poleBrush As New SolidBrush(yellowBase),
              darkPlate As New SolidBrush(Color.FromArgb(30, 30, 32))

            g.FillRectangle(poleBrush, bounds.X, bounds.Y, bounds.Width, bounds.Height * 2 + 4)
            g.DrawRectangle(Pens.Black, bounds.X, bounds.Y, bounds.Width, bounds.Height * 2 + 4)

            Dim displayFace As New Rectangle(bounds.X + 2, bounds.Y + 2, bounds.Width - 4, bounds.Height - 4)
            g.FillRectangle(darkPlate, displayFace)

            Dim topLensColor As Color = Color.FromArgb(60, 0, 0)
            Dim bottomLensColor As Color = Color.FromArgb(0, 50, 0)

            If pedWalkActive Then
                bottomLensColor = Color.FromArgb(0, 255, 100)
            Else
                topLensColor = Color.FromArgb(255, 20, 20)
            End If

            Dim bulbRadius As Integer = (displayFace.Height \ 2) - 2
            Using topLight As New SolidBrush(topLensColor),
                  bottomLight As New SolidBrush(bottomLensColor)

                g.FillEllipse(topLight, displayFace.X + (displayFace.Width \ 2) - (bulbRadius \ 2), displayFace.Y + 1, bulbRadius, bulbRadius)
                g.FillEllipse(bottomLight, displayFace.X + (displayFace.Width \ 2) - (bulbRadius \ 2), displayFace.Y + (displayFace.Height \ 2) + 1, bulbRadius, bulbRadius)
            End Using

            Dim buttonArea As New Rectangle(bounds.X, bounds.Y + bounds.Height + 2, bounds.Width, bounds.Height)
            g.DrawLine(Pens.Black, buttonArea.X, buttonArea.Y, buttonArea.X + buttonArea.Width, buttonArea.Y)

            Dim isRequested As Boolean = (isVerticalLight AndAlso nsPedRequested) Or (Not isVerticalLight AndAlso ewPedRequested)
            Dim buttonColor As Color = If(isRequested, Color.FromArgb(10, 255, 50), Color.FromArgb(210, 40, 30))

            Using plungerBrush As New SolidBrush(buttonColor)
                g.FillEllipse(plungerBrush, buttonArea.X + 3, buttonArea.Y + 3, buttonArea.Width - 6, buttonArea.Height - 6)
                g.DrawEllipse(Pens.Black, buttonArea.X + 3, buttonArea.Y + 3, bounds.Width - 6, bounds.Height - 6)
            End Using
        End Using

        Dim vOffsetW As Integer = If(isVerticalLight, 18, 40)
        Dim vOffsetH As Integer = If(isVerticalLight, 40, 18)

        Dim vx As Integer = X
        Dim vy As Integer = Y

        If isVerticalLight Then
            vx += If(dirX < 0, 2, size - 20)
            vy += If(dirY < 0, 2, size - 42)
        Else
            vx += If(dirX < 0, 2, size - 42)
            vy += If(dirY < 0, 2, size - 20)
        End If

        Using backplateBrush As New SolidBrush(Color.FromArgb(25, 25, 25))
            g.FillRectangle(backplateBrush, vx, vy, vOffsetW, vOffsetH)
            g.DrawRectangle(Pens.Black, vx, vy, vOffsetW, vOffsetH)
        End Using

        Dim rX As Integer = vx + 3
        Dim rY As Integer = vy + 3
        Dim yX As Integer = If(isVerticalLight, vx + 3, vx + 14)
        Dim yY As Integer = If(isVerticalLight, vy + 14, vy + 3)
        Dim gX As Integer = If(isVerticalLight, vx + 3, vx + 25)
        Dim gY As Integer = If(isVerticalLight, vy + 25, vy + 3)

        Dim cRed As Color = If(vehicleState = 0, Color.FromArgb(255, 15, 15), Color.FromArgb(55, 0, 0))
        Dim cYellow As Color = If(vehicleState = 1, Color.FromArgb(255, 215, 0), Color.FromArgb(55, 45, 0))
        Dim cGreen As Color = If(vehicleState = 2, Color.FromArgb(0, 250, 50), Color.FromArgb(0, 55, 5))

        Using b As New SolidBrush(cRed)
            g.FillEllipse(b, rX, rY, 11, 11)
            If vehicleState = 0 Then
                Using p As New Pen(Color.FromArgb(120, 255, 50, 50), 1)
                    g.DrawEllipse(p, rX - 1, rY - 1, 13, 13)
                End Using
            End If
        End Using

        Using b As New SolidBrush(cYellow)
            g.FillEllipse(b, yX, yY, 11, 11)
            If vehicleState = 1 Then
                Using p As New Pen(Color.FromArgb(120, 255, 215, 0), 1)
                    g.DrawEllipse(p, yX - 1, yY - 1, 13, 13)
                End Using
            End If
        End Using

        Using b As New SolidBrush(cGreen)
            g.FillEllipse(b, gX, gY, 11, 11)
            If vehicleState = 2 Then
                Using p As New Pen(Color.FromArgb(120, 50, 255, 50), 1)
                    g.DrawEllipse(p, gX - 1, gY - 1, 13, 13)
                End Using
            End If
        End Using
    End Sub
End Class